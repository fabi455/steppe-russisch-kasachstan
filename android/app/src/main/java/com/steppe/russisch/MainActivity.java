package com.steppe.russisch;

import android.app.Activity;
import android.content.Intent;
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
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;

/** Self-contained, offline, app-only WebView. No INTERNET permission or trackers. */
public class MainActivity extends Activity {
    private static final int PICK_FILE = 101;
    private static final int EXPORT_FILE = 102;
    private WebView web;
    private ValueCallback<Uri[]> pendingFileChoice;
    private String pendingExport;

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
                return !("file".equals(u.getScheme()) && "/android_asset/index.html".equals(u.getPath()));
            }
        });
        web.setWebChromeClient(new WebChromeClient() {
            @Override public boolean onShowFileChooser(WebView view, ValueCallback<Uri[]> callback, FileChooserParams params) {
                if (pendingFileChoice != null) pendingFileChoice.onReceiveValue(null);
                pendingFileChoice = callback;
                Intent intent = new Intent(Intent.ACTION_GET_CONTENT);
                intent.setType("application/json");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                try {startActivityForResult(Intent.createChooser(intent,"Lernstand importieren"),PICK_FILE);}
                catch(Exception ex) {pendingFileChoice.onReceiveValue(null);pendingFileChoice=null;return false;}
                return true;
            }
        });
        web.loadUrl("file:///android_asset/index.html");
    }
    private final class LocalFiles {
        @JavascriptInterface public void exportProgress(String json) {
            if(json==null || json.length()>5_000_000)return;
            runOnUiThread(() -> {
                pendingExport=json;
                Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT);
                intent.setType("application/json");
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.putExtra(Intent.EXTRA_TITLE,"steppe-russisch-lernstand.json");
                try {startActivityForResult(intent,EXPORT_FILE);} catch(Exception ignored){pendingExport=null;}
            });
        }
    }
    @Override protected void onActivityResult(int code,int result,Intent data) {
        super.onActivityResult(code,result,data);
        if(code==PICK_FILE){
            if(pendingFileChoice!=null){Uri[] uris=result==RESULT_OK && data!=null && data.getData()!=null ? new Uri[]{data.getData()}:null;
                pendingFileChoice.onReceiveValue(uris);pendingFileChoice=null;}
        }
        if(code==EXPORT_FILE){
            if(result==RESULT_OK && data!=null && data.getData()!=null && pendingExport!=null){
                try(OutputStream out=getContentResolver().openOutputStream(data.getData())) {
                    if(out!=null)out.write(pendingExport.getBytes(StandardCharsets.UTF_8));
                } catch(Exception ignored){}
            }
            pendingExport=null;
        }
    }
    @Override public void onBackPressed(){
        if(web!=null && web.canGoBack())web.goBack();else super.onBackPressed();
    }
    @Override protected void onDestroy(){if(web!=null){web.removeJavascriptInterface("SteppeAndroid");web.destroy();}super.onDestroy();}
}
