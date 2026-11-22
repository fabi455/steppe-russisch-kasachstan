package com.steppe.russisch;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.media.MediaPlayer;
import android.media.PlaybackParams;
import android.net.Uri;
import android.os.Bundle;
import android.view.View;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import org.json.JSONArray;
import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Set;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

/**
 * Steppe – offline Android learning app with verified optional content packs.
 *
 * Data updates are downloaded from the owner's GitHub release and installed
 * privately without replacing executable JavaScript or Android code.
 * Android code updates require a separately signed APK (same signing key).
 */
public class MainActivity extends Activity {
    private static final int PICK_FILE = 101;
    private static final int EXPORT_FILE = 102;
    private static final String CONTENT_CATALOG =
        "https://raw.githubusercontent.com/fabi455/steppe-russisch-kasachstan/main/updates/latest.json";
    private static final String CONTENT_PACK =
        "https://github.com/fabi455/steppe-russisch-kasachstan/releases/download/content-latest/steppe-content.zip";
    private static final String RELEASES_PAGE =
        "https://github.com/fabi455/steppe-russisch-kasachstan/releases";
    private static final long CHECK_INTERVAL_MS = 24L * 60 * 60 * 1000;
    private static final int MAX_ZIP = 24 * 1024 * 1024;
    private static final int MAX_EXPANDED = 50 * 1024 * 1024;
    private static final int MAX_JSON = 2 * 1024 * 1024;
    private static final int MAX_AUDIO = 1024 * 1024;

    private final AtomicBoolean updating = new AtomicBoolean(false);
    private final ExecutorService executor = Executors.newSingleThreadExecutor();
    private WebView web;
    private MediaPlayer player;
    private ValueCallback<Uri[]> pendingFileChoice;
    private String pendingExport;

    private File activeContent() { return new File(getFilesDir(), "steppe-content"); }
    private SharedPreferences preferences() {
        return getSharedPreferences("steppe-update-settings", MODE_PRIVATE);
    }
    private static boolean isValidId(String id) {
        return id != null && id.matches("[A-Za-z0-9_-]{1,80}");
    }

    @Override public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        getWindow().setStatusBarColor(android.graphics.Color.rgb(11,61,86));
        getWindow().setNavigationBarColor(android.graphics.Color.rgb(245,248,250));
        getWindow().getDecorView().setSystemUiVisibility(View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR);
        web = new WebView(this);
        web.setBackgroundColor(android.graphics.Color.rgb(245,248,250));
        setContentView(web);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setAllowContentAccess(true);
        s.setAllowFileAccessFromFileURLs(false);
        s.setAllowUniversalAccessFromFileURLs(false);
        s.setMediaPlaybackRequiresUserGesture(true);
        web.addJavascriptInterface(new LocalFiles(), "SteppeAndroid");
        web.setWebViewClient(new WebViewClient() {
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                Uri u = request.getUrl();
                // No untrusted remote HTML or JS is ever loaded into the learning WebView.
                return !("file".equals(u.getScheme()) &&
                        (u.getPath() != null && u.getPath().startsWith("/android_asset/")));
            }
            @Override public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                long last = preferences().getLong("lastCheck", 0);
                if(System.currentTimeMillis()-last > CHECK_INTERVAL_MS) {
                    executor.execute(() -> checkContent(false));
                }
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if(pendingFileChoice != null) pendingFileChoice.onReceiveValue(null);
                pendingFileChoice=callback;
                Intent intent=new Intent(Intent.ACTION_GET_CONTENT);
                intent.setType("application/json");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                try {startActivityForResult(Intent.createChooser(intent,"Lernstand importieren"),PICK_FILE);}
                catch(Exception ex){pendingFileChoice.onReceiveValue(null);pendingFileChoice=null;return false;}
                return true;
            }
        });
        web.loadUrl("file:///android_asset/index.html");
    }

    private String readUtf8(File file, int maxBytes) throws Exception {
        try(InputStream in = new FileInputStream(file)) {
            return new String(readLimited(in, maxBytes), StandardCharsets.UTF_8);
        }
    }
    private static byte[] readLimited(InputStream stream, int maxBytes) throws Exception {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[8192]; int n;
        while((n=stream.read(buf))!=-1) {
            if(out.size()+n > maxBytes) throw new Exception("Datei überschreitet die Größenbegrenzung");
            out.write(buf,0,n);
        }
        return out.toByteArray();
    }
    private String bundledContent() throws Exception {
        try(InputStream in = getAssets().open("content.json")) {
            return new String(readLimited(in, MAX_JSON),StandardCharsets.UTF_8);
        }
    }
    private long bundledRevision() {
        try(InputStream in = getAssets().open("updates/update-revision.json")) {
            JSONObject o = new JSONObject(new String(readLimited(in, 2048), StandardCharsets.UTF_8));
            return o.optLong("revision",0);
        } catch(Exception ignored) { return 0; }
    }
    private long installedRevision() {
        File installed = new File(activeContent(),"update-revision.json");
        if(installed.isFile())try {
            return new JSONObject(readUtf8(installed,2048)).optLong("revision",0);
        }catch(Exception ignored){}
        return bundledRevision();
    }
    private String installedLessons() {
        File json = new File(activeContent(),"content.json");
        if(!json.isFile())return "";
        try { return readUtf8(json,MAX_JSON); } catch(Exception ignored){ return ""; }
    }
    private File downloadedAudio(String id) {
        if(!isValidId(id))return null;
        File file=new File(activeContent(), "audio/"+id+".mp3");
        return file.isFile() ? file : null;
    }

    private String getApplicationVersion() {
        try { return getPackageManager().getPackageInfo(getPackageName(),0).versionName; }
        catch(Exception ignored) { return "unbekannt"; }
    }
    private final class LocalFiles {
        @JavascriptInterface public String getUpdatedContent() {
            return installedLessons();
        }
        @JavascriptInterface public boolean hasUpdatedAudio(String id) {
            return downloadedAudio(id)!=null;
        }
        @JavascriptInterface public void playUpdatedAudio(String id, boolean slow) {
            File file=downloadedAudio(id);
            if(file==null)return;
            runOnUiThread(()->{
                try {
                    if(player!=null){player.stop();player.release();player=null;}
                    player=new MediaPlayer();
                    player.setDataSource(file.getAbsolutePath());
                    player.setOnCompletionListener(mp->{mp.release();if(player==mp)player=null;});
                    player.prepare();
                    if(slow && android.os.Build.VERSION.SDK_INT>=23)
                        player.setPlaybackParams(new PlaybackParams().setSpeed(0.85f));
                    else player.start();
                } catch(Exception ignored) {
                    if(player!=null){player.release();player=null;}
                    status("Audio konnte nicht abgespielt werden.",false);
                }
            });
        }
        @JavascriptInterface public void checkContentUpdates() {
            executor.execute(()->checkContent(true));
        }
        @JavascriptInterface public String getUpdateInfo() {
            return "Inhalte: Revision "+installedRevision()+" · App: "+getApplicationVersion();
        }
        @JavascriptInterface public void openAppUpdates() {
            runOnUiThread(()->{
                try {
                    Intent i=new Intent(Intent.ACTION_VIEW, Uri.parse(RELEASES_PAGE));
                    startActivity(i);
                } catch(Exception ignored){status("GitHub konnte nicht geöffnet werden.",false);}
            });
        }
        @JavascriptInterface public void exportProgress(String json) {
            if(json==null || json.length()>5_000_000)return;
            runOnUiThread(()->{
                pendingExport=json;
                Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.setType("application/json");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.putExtra(Intent.EXTRA_TITLE,"steppe-russisch-lernstand.json");
                try{startActivityForResult(intent,EXPORT_FILE);}catch(Exception ignored){pendingExport=null;}
            });
        }
    }

    private void status(String message, boolean updated) {
        runOnUiThread(()->{
            if(web==null)return;
            String script="if(window.SteppeUpdates&&SteppeUpdates.status)SteppeUpdates.status("+
                    JSONObject.quote(message)+","+(updated?"true":"false")+");";
            web.evaluateJavascript(script,null);
        });
    }
    private static String sha256(byte[] bytes) throws Exception {
        byte[] hash=MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder sb=new StringBuilder();
        for(byte b:hash)sb.append(String.format(java.util.Locale.ROOT,"%02x", b&0xff));
        return sb.toString();
    }
    private static byte[] download(String url,int max) throws Exception {
        URL next=new URL(url);
        for(int redirect=0;redirect<5;redirect++){
            if(!"https".equals(next.getProtocol()))throw new Exception("Unsichere Update-Adresse");
            String host=next.getHost().toLowerCase(java.util.Locale.ROOT);
            if(!(host.equals("github.com")||host.equals("raw.githubusercontent.com")
                ||host.endsWith(".githubusercontent.com")||host.endsWith(".github.com")))
                throw new Exception("Unbekannter Update-Server");
            HttpURLConnection conn=(HttpURLConnection)next.openConnection();
            conn.setInstanceFollowRedirects(false);
            conn.setRequestProperty("User-Agent","Steppe-Russisch-Android-Update");
            conn.setConnectTimeout(12000);conn.setReadTimeout(25000);
            try{
                int code=conn.getResponseCode();
                if(code>=300 && code<400){
                    String location=conn.getHeaderField("Location");
                    if(location==null)throw new Exception("Update-Weiterleitung ohne Ziel");
                    next=new URL(next,location);
                    continue;
                }
                if(code!=200)throw new Exception("Serverantwort: HTTP "+code);
                try(InputStream in=conn.getInputStream()){return readLimited(in,max);}
            }finally{conn.disconnect();}
        }
        throw new Exception("Zu viele Update-Weiterleitungen");
    }
    private static void deleteTree(File file) {
        if(!file.exists())return;
        if(file.isDirectory()){
            File[] files=file.listFiles();
            if(files!=null)for(File x:files)deleteTree(x);
        }
        file.delete();
    }
    private static boolean validMp3(File f) throws Exception {
        if(!f.isFile() || f.length()<1500 || f.length()>MAX_AUDIO)return false;
        try(InputStream in=new FileInputStream(f)){
            int a=in.read(),b=in.read(),c=in.read();
            return (a=='I'&&b=='D'&&c=='3') || (a==255 && (b&224)==224);
        }
    }
    private static Set<String> checkedIds(JSONArray lessons) throws Exception {
        if(lessons.length()<1 || lessons.length()>150)throw new Exception("Ungültiger Lektionsumfang");
        Set<String> result=new HashSet<>();
        for(int i=0;i<lessons.length();i++){
            JSONObject lesson=lessons.getJSONObject(i);
            String lid=lesson.getString("id");
            if(!isValidId(lid))throw new Exception("Ungültige Lektionskennung");
            for(String section:new String[]{"words","phrases"}){
                JSONArray words=lesson.getJSONArray(section);
                if(words.length()>300)throw new Exception("Lektion enthält zu viele Einträge");
                for(int j=0;j<words.length();j++){
                    JSONObject w=words.getJSONObject(j);
                    String id=w.getString("id");
                    String term=w.getString("term"),meaning=w.getString("meaning");
                    if(!isValidId(id)||term.isEmpty()||term.length()>350||meaning.isEmpty()||meaning.length()>800
                       ||!result.add(id))throw new Exception("Ungültige Wörterbuchdaten");
                }
            }
        }
        if(result.size()>10000)throw new Exception("Zu viele Wörter");
        return result;
    }
    private static void extractVerified(byte[] zip, File folder, long revision) throws Exception {
        if(!folder.mkdir())throw new Exception("Update-Ziel konnte nicht erstellt werden");
        int uncompressed=0,files=0;
        try(ZipInputStream zs=new ZipInputStream(new java.io.ByteArrayInputStream(zip))){
            ZipEntry item;
            while((item=zs.getNextEntry())!=null){
                if(item.isDirectory())continue;
                String name=item.getName();
                if(!(name.equals("content.json")||name.equals("update-revision.json")||
                     name.matches("audio/[A-Za-z0-9_-]{1,80}\\.mp3")))
                    throw new Exception("Unerlaubte Datei im Update-Paket");
                File file=new File(folder,name);
                if(!file.getCanonicalPath().startsWith(folder.getCanonicalPath()+File.separator))
                    throw new Exception("Ungültiger Dateipfad im Update-Paket");
                File parent=file.getParentFile();
                if(!parent.exists()&&!parent.mkdirs())throw new Exception("Ordner konnte nicht erstellt werden");
                if(file.exists())throw new Exception("Doppelte Datei im Update-Paket");
                int limit=name.equals("content.json")?MAX_JSON:name.equals("update-revision.json")?2048:MAX_AUDIO;
                try(OutputStream out=new FileOutputStream(file)){
                    byte[] bytes=new byte[8192];int n,total=0;
                    while((n=zs.read(bytes))!=-1){
                        total+=n;uncompressed+=n;
                        if(total>limit||uncompressed>MAX_EXPANDED)throw new Exception("Update-Paket ist zu groß");
                        out.write(bytes,0,n);
                    }
                }
                files++;
                if(files>10200)throw new Exception("Zu viele Dateien im Update-Paket");
                zs.closeEntry();
            }
        }
        JSONObject local=new JSONObject(readFileUtf8(new File(folder,"update-revision.json"),2048));
        if(local.getLong("revision")!=revision)throw new Exception("Versionsnummer stimmt nicht überein");
    }
    private static String readFileUtf8(File file,int limit) throws Exception {
        try(InputStream in=new FileInputStream(file)){
            return new String(readLimited(in,limit),StandardCharsets.UTF_8);
        }
    }

    private void checkContent(boolean manual) {
        if(!updating.compareAndSet(false,true)){if(manual)status("Update-Prüfung läuft bereits.",false);return;}
        try {
            byte[] source=download(CONTENT_CATALOG,16*1024);
            JSONObject manifest=new JSONObject(new String(source,StandardCharsets.UTF_8));
            if(manifest.getInt("schema")!=1)throw new Exception("Update-Format nicht unterstützt");
            long revision=manifest.getLong("revision");
            if(revision<=installedRevision()){
                preferences().edit().putLong("lastCheck",System.currentTimeMillis()).apply();
                if(manual)status("Deine Lerninhalte sind bereits aktuell.",false);
                return;
            }
            String expected=manifest.getString("sha256").toLowerCase(java.util.Locale.ROOT);
            if(!expected.matches("[a-f0-9]{64}"))throw new Exception("Ungültige Paket-Prüfsumme");
            int declaredSize=manifest.getInt("size");
            if(declaredSize<100000||declaredSize>MAX_ZIP)throw new Exception("Ungültige Paketgröße");
            if(manual)status("Neue Lerninhalte gefunden. Download wird geprüft …",false);
            byte[] zip=download(CONTENT_PACK,MAX_ZIP);
            if(zip.length!=declaredSize || !sha256(zip).equals(expected))
                throw new Exception("Prüfsumme stimmt nicht überein");
            File scratch=new File(getFilesDir(),"steppe-update-temp");
            deleteTree(scratch);
            try {
                extractVerified(zip,scratch,revision);
                Set<String> oldIds=checkedIds(new JSONArray(bundledContent()));
                Set<String> ids=checkedIds(new JSONArray(readUtf8(new File(scratch,"content.json"),MAX_JSON)));
                if(!ids.containsAll(oldIds))throw new Exception("Update würde vorhandene Lernkarten entfernen");
                File[] mp3s=new File(scratch,"audio").listFiles();
                if(mp3s==null||mp3s.length!=ids.size())throw new Exception("Hörproben unvollständig");
                for(String id:ids){
                    if(!validMp3(new File(scratch,"audio/"+id+".mp3")))
                        throw new Exception("Ungültige Hörprobe: "+id);
                }
                File active=activeContent(),old=new File(getFilesDir(),"steppe-content-backup");
                deleteTree(old);
                if(active.exists()&&!active.renameTo(old))
                    throw new Exception("Vorherige Lerninhalte konnten nicht gesichert werden");
                if(!scratch.renameTo(active)){
                    if(old.exists())old.renameTo(active);
                    throw new Exception("Lerninhalte konnten nicht aktiviert werden");
                }
                deleteTree(old);
            }finally{deleteTree(scratch);}
            preferences().edit().putLong("lastCheck",System.currentTimeMillis()).apply();
            status("Neue Wörter, Lektionen und Hörproben sind bereit! Starte den Lernbereich neu, um sie zu nutzen.",true);
        } catch(Exception e){
            if(manual)status("Inhalte konnten nicht aktualisiert werden: "+e.getMessage(),false);
        } finally{updating.set(false);}
    }

    @Override protected void onActivityResult(int code,int result,Intent data) {
        super.onActivityResult(code,result,data);
        if(code==PICK_FILE && pendingFileChoice!=null){
            Uri[] uris=result==RESULT_OK && data!=null && data.getData()!=null ? new Uri[]{data.getData()}:null;
            pendingFileChoice.onReceiveValue(uris);pendingFileChoice=null;
        }
        if(code==EXPORT_FILE){
            if(result==RESULT_OK && data!=null && data.getData()!=null && pendingExport!=null){
                try(OutputStream out=getContentResolver().openOutputStream(data.getData())){
                    if(out!=null)out.write(pendingExport.getBytes(StandardCharsets.UTF_8));
                }catch(Exception ignored){}
            }
            pendingExport=null;
        }
    }
    @Override public void onBackPressed(){
        if(web!=null && web.canGoBack())web.goBack();else super.onBackPressed();
    }
    @Override protected void onDestroy(){
        executor.shutdownNow();
        if(player!=null){player.release();player=null;}
        if(web!=null){web.removeJavascriptInterface("SteppeAndroid");web.destroy();}
        super.onDestroy();
    }
}
