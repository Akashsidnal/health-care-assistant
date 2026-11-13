package com.medicare.cloud

import android.annotation.SuppressLint
import android.app.AlertDialog
import android.content.Context
import android.content.SharedPreferences
import android.graphics.Bitmap
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.os.Bundle
import android.view.KeyEvent
import android.view.View
import android.webkit.*
import android.widget.EditText
import android.widget.ProgressBar
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar
    private lateinit var prefs: SharedPreferences

    companion object {
        private const val PREFS_NAME = "MediCareCloudPrefs"
        private const val KEY_SERVER_URL = "server_url"
        private const val DEFAULT_URL = "http://10.177.166.250:5000"
    }

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

        // Setup UI layout programmatically
        val rootLayout = android.widget.RelativeLayout(this).apply {
            layoutParams = android.widget.RelativeLayout.LayoutParams(
                android.widget.RelativeLayout.LayoutParams.MATCH_PARENT,
                android.widget.RelativeLayout.LayoutParams.MATCH_PARENT
            )
        }

        progressBar = ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal).apply {
            layoutParams = android.widget.RelativeLayout.LayoutParams(
                android.widget.RelativeLayout.LayoutParams.MATCH_PARENT,
                10
            )
            isIndeterminate = false
            max = 100
            visibility = View.GONE
        }

        webView = WebView(this).apply {
            layoutParams = android.widget.RelativeLayout.LayoutParams(
                android.widget.RelativeLayout.LayoutParams.MATCH_PARENT,
                android.widget.RelativeLayout.LayoutParams.MATCH_PARENT
            )
        }

        rootLayout.addView(webView)
        rootLayout.addView(progressBar)
        setContentView(rootLayout)

        configureWebView()

        val savedUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
        if (isNetworkAvailable()) {
            webView.loadUrl(savedUrl)
        } else {
            showOfflineMessage(savedUrl)
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private fun configureWebView() {
        val settings = webView.settings
        settings.javaScriptEnabled = true
        settings.domStorageEnabled = true
        settings.databaseEnabled = true
        settings.allowFileAccess = true
        settings.allowContentAccess = true
        settings.cacheMode = WebSettings.LOAD_DEFAULT
        settings.useWideViewPort = true
        settings.loadWithOverviewMode = true
        settings.mediaPlaybackRequiresUserGesture = false // Real-time audio alarms

        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                if (newProgress < 100) {
                    progressBar.visibility = View.VISIBLE
                    progressBar.progress = newProgress
                } else {
                    progressBar.visibility = View.GONE
                }
            }

            override fun onJsAlert(view: WebView?, url: String?, message: String?, result: JsResult?): Boolean {
                AlertDialog.Builder(this@MainActivity)
                    .setTitle("MediCare Cloud")
                    .setMessage(message)
                    .setPositiveButton("OK") { _, _ -> result?.confirm() }
                    .setCancelable(false)
                    .show()
                return true
            }
        }

        webView.webViewClient = object : WebViewClient() {
            override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                super.onPageStarted(view, url, favicon)
                progressBar.visibility = View.VISIBLE
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                progressBar.visibility = View.GONE
            }

            override fun onReceivedError(view: WebView?, errorCode: Int, description: String?, failingUrl: String?) {
                showServerConfigDialog("Unable to connect to $failingUrl: $description")
            }
        }
    }

    private fun showServerConfigDialog(errorMessage: String? = null) {
        val currentUrl = prefs.getString(KEY_SERVER_URL, DEFAULT_URL) ?: DEFAULT_URL
        val input = EditText(this).apply {
            setText(currentUrl)
            setHint("http://192.168.x.x:5000")
        }

        AlertDialog.Builder(this)
            .setTitle("MediCare Cloud Server IP")
            .setMessage((if (errorMessage != null) "$errorMessage\n\n" else "") +
                    "Enter the host computer's Wi-Fi / LAN IP address running the MediCare Cloud server:")
            .setView(input)
            .setPositiveButton("Connect") { _, _ ->
                val newUrl = input.text.toString().trim()
                if (newUrl.isNotEmpty()) {
                    prefs.edit().putString(KEY_SERVER_URL, newUrl).apply()
                    webView.loadUrl(newUrl)
                }
            }
            .setNegativeButton("Retry") { _, _ ->
                webView.loadUrl(currentUrl)
            }
            .setCancelable(true)
            .show()
    }

    private fun showOfflineMessage(targetUrl: String) {
        Toast.makeText(this, "No internet connection detected. Please connect to Wi-Fi.", Toast.LENGTH_LONG).show()
        showServerConfigDialog("Network unavailable")
    }

    private fun isNetworkAvailable(): Boolean {
        val cm = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val nw = cm.activeNetwork ?: return false
        val actNw = cm.getNetworkCapabilities(nw) ?: return false
        return actNw.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }

    override fun onKeyDown(keyCode: Int, event: KeyEvent?): Boolean {
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack()
            return true
        }
        return super.onKeyDown(keyCode, event)
    }
}
