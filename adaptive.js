/* Steppe 1.3: adaptive spaced practice. All progress stays on the device. */
window.STEPPE_ADAPTIVE = (() => {
  'use strict';
  const now = () => Date.now();
  const init = s => {if(!s.learningStats || typeof s.learningStats !== 'object')s.learningStats={};if(!s.reviews || typeof s.reviews !== 'object')s.reviews={};return s;};
  function measure(state,w){
    init(state);
    const s=state.learningStats[w.id]||{}, r=state.reviews[w.id]||{};
    return {seen:Number(s.seen||0),correct:Number(s.correct||0),wrong:Number(s.wrong||0),
      streak:Number(s.streak||0),reps:Number(r.reps||0),
      due:!!(s.seen||r.reps) && Number(r.next||0)<=now(),
      fresh:!(s.seen||r.reps)};
  }
  function priority(state,w){
    const x=measure(state,w);
    if(x.wrong && x.wrong>=x.correct) return 115+Math.min(20,x.wrong*3);
    if(x.due) return 96+Math.max(0,3-x.streak)*3;
    if(x.fresh)return 73;
    if(x.streak<2)return 51;
    return Math.max(1,30-x.streak*5-x.reps*2);
  }
  function pick(state,lesson,limit=12){
    if(!lesson)return [];
    const pool=[...lesson.words,...lesson.phrases]
      .map((w,i)=>({w,p:priority(state,w),tie:Math.random(),i}))
      .sort((a,b)=>b.p-a.p||a.tie-b.tie);
    const chosen=pool.slice(0,Math.min(limit,pool.length)).map(x=>x.w);
    if(chosen.length>=6 && chosen.every(w=>priority(state,w)>=90)){
      const spare=pool.find(x=>x.p<90);
      if(spare)chosen.splice(chosen.length-2,1,spare.w);
    }
    return chosen;
  }
  function grade(state,w,good){
    init(state);
    const s=state.learningStats[w.id]||{seen:0,correct:0,wrong:0,streak:0};
    s.seen=Number(s.seen||0)+1;
    if(good){s.correct=Number(s.correct||0)+1;s.streak=Number(s.streak||0)+1;}
    else{s.wrong=Number(s.wrong||0)+1;s.streak=0;}
    s.last=now();state.learningStats[w.id]=s;
    const r=state.reviews[w.id]||{reps:0,interval:0,ease:2.5};
    r.ease=Number(r.ease)||2.5;
    if(good){
      r.reps=Number(r.reps||0)+1;
      r.interval=r.reps===1?1:r.reps===2?3:Math.max(4,Math.round((Number(r.interval)||3)*r.ease));
      r.ease=Math.min(3,Number((r.ease+0.05).toFixed(2)));
      r.next=now()+r.interval*86400000;
    }else{
      r.reps=0;r.interval=0;r.ease=Math.max(1.3,r.ease-0.2);
      r.next=now()+10*60*1000;
    }
    state.reviews[w.id]=r;
  }
  function stats(state,lesson){
    if(!lesson)return {due:0,weak:0,mastered:0,fresh:0,total:0};
    const result={due:0,weak:0,mastered:0,fresh:0,total:0};
    for(const w of [...lesson.words,...lesson.phrases]){
      result.total++;const m=measure(state,w);
      if(m.fresh)result.fresh++;
      else if(m.wrong>m.correct || (m.wrong>0 && m.streak<2))result.weak++;
      else if(m.streak>=3||m.reps>=3)result.mastered++;
      if(m.due)result.due++;
    }
    return result;
  }
  function suggested(state,lessons){
    const first=lessons.findIndex(l=>!state.completed?.[l.id]);
    const problematic=lessons.map((l,i)=>({i,s:stats(state,l)}))
      .filter(({i,s})=>state.completed?.[lessons[i].id]&&(s.weak>=3||s.due>=6))
      .sort((a,b)=>(b.s.weak*2+b.s.due)-(a.s.weak*2+a.s.due));
    return problematic.length?problematic[0].i:(first===-1?Math.max(0,lessons.length-1):first);
  }
  return {init,measure,priority,pick,grade,stats,suggested};
})();
