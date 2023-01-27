package xyz.zedler.patrick.grocy.activity;

/*
    This file is part of Grocy Android.

    Grocy Android is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Grocy Android is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Grocy Android.  If not, see <http://www.gnu.org/licenses/>.

    Copyright 2020 by Patrick Zedler & Dominic Zedler
*/

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.webkit.URLUtil;

import androidx.appcompat.app.AppCompatActivity;
import androidx.fragment.app.Fragment;
import androidx.fragment.app.FragmentManager;
import androidx.preference.PreferenceManager;

import com.android.volley.AuthFailureError;
import com.android.volley.NoConnectionError;
import com.android.volley.ServerError;
import com.android.volley.TimeoutError;
import com.google.android.material.bottomsheet.BottomSheetDialogFragment;
import com.google.android.material.snackbar.Snackbar;

import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Arrays;

import xyz.zedler.patrick.grocy.R;
import xyz.zedler.patrick.grocy.api.GrocyApi;
import xyz.zedler.patrick.grocy.databinding.ActivityLoginBinding;
import xyz.zedler.patrick.grocy.fragment.bottomSheetDialog.CompatibilityBottomSheetDialogFragment;
import xyz.zedler.patrick.grocy.fragment.bottomSheetDialog.FeedbackBottomSheetDialogFragment;
import xyz.zedler.patrick.grocy.fragment.bottomSheetDialog.MessageBottomSheetDialogFragment;
import xyz.zedler.patrick.grocy.helper.DownloadHelper;
import xyz.zedler.patrick.grocy.util.ClickUtil;
import xyz.zedler.patrick.grocy.util.ConfigUtil;
import xyz.zedler.patrick.grocy.util.Constants;
import xyz.zedler.patrick.grocy.util.NetUtil;

public class LoginActivity extends AppCompatActivity {

    final static String TAG = LoginActivity.class.getSimpleName();
    private final static boolean DEBUG = false;

    private SharedPreferences sharedPrefs;
    private SharedPreferences credentials;
    private DownloadHelper dlHelper;
    private FragmentManager fragmentManager;
    private ActivityLoginBinding binding;
    private ClickUtil clickUtil = new ClickUtil();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        binding = ActivityLoginBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        sharedPrefs = PreferenceManager.getDefaultSharedPreferences(this);
        credentials = getSharedPreferences(Constants.PREF.CREDENTIALS, Context.MODE_PRIVATE);

        fragmentManager = getSupportFragmentManager();

        // WEB REQUESTS

        dlHelper = new DownloadHelper(this, TAG);

        // INITIALIZE VIEWS

        if(credentials.getString(Constants.PREF.SERVER_URL, null) != null) {
            binding.editTextLoginServer.setText(
                    credentials.getString(Constants.PREF.SERVER_URL, null)
            );
        }
        binding.editTextLoginKey.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) {}
            public void afterTextChanged(Editable s) {
                if(binding.textInputLoginKey.isErrorEnabled()) {
                    binding.textInputLoginKey.setErrorEnabled(false);
                }
            }
        });

        if(credentials.getString(Constants.PREF.API_KEY, null) != null) {
            binding.editTextLoginKey.setText(
                    credentials.getString(Constants.PREF.API_KEY, null)
            );
        }
        binding.editTextLoginServer.addTextChangedListener(new TextWatcher() {
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {}
            public void onTextChanged(CharSequence s, int start, int before, int count) {}
            public void afterTextChanged(Editable s) {
                if(binding.textInputLoginServer.isErrorEnabled()) {
                    binding.textInputLoginServer.setErrorEnabled(false);
                }
            }
        });

        binding.buttonLoginKey.setOnClickListener(v -> {
            if(clickUtil.isDisabled()) return;
            if(getServer().isEmpty()) {
                binding.textInputLoginServer.setError(getString(R.string.error_empty));
            } else if(!URLUtil.isValidUrl(getServer())) {
                binding.textInputLoginServer.setError(getString(R.string.error_invalid_url));
            } else {
                binding.textInputLoginServer.setErrorEnabled(false);

                Intent browserManageKeys = new Intent(Intent.ACTION_VIEW);
                Uri uri = Uri.parse(getServer() + "/manageapikeys");
                browserManageKeys.setData(uri);
                startActivity(browserManageKeys);
            }
        });

        binding.buttonLoginLogin.setOnClickListener(v -> {
            if(clickUtil.isDisabled()) return;

            // remove old errors
            binding.textInputLoginServer.setErrorEnabled(false);
            binding.textInputLoginKey.setErrorEnabled(false);

            String server = getServer();
            if(server.isEmpty()) {
                binding.textInputLoginServer.setError(getString(R.string.error_empty));
            } else if(!URLUtil.isNetworkUrl(server)) {
                binding.textInputLoginServer.setError(getString(R.string.error_invalid_url));
            } else {
                requestLogin(server, getKey(), true, false);
            }
        });

        binding.buttonLoginDemo.setOnClickListener(v -> {
            if(clickUtil.isDisabled()) return;
            requestLogin(getString(R.string.url_grocy_demo), "", true, true);
        });

        binding.buttonLoginHelp.setTooltipText(getString(R.string.title_help));
        binding.buttonLoginHelp.setOnClickListener(v -> {
            if(clickUtil.isDisabled()) return;
            binding.buttonLoginHelp.startIconAnimation();
            new Handler().postDelayed(() -> {
                boolean success = NetUtil.openURL(this, Constants.URL.HELP);
                if(!success) {
                    Snackbar.make(
                            binding.coordinatorLoginContainer,
                            R.string.error_no_browser,
                            Snackbar.LENGTH_LONG
                    ).show();
                }
            }, 300);
        });

        binding.buttonLoginFeedback.setTooltipText(getString(R.string.title_feedback));
        binding.buttonLoginFeedback.setOnClickListener(v -> {
            if(clickUtil.isDisabled()) return;
            binding.buttonLoginFeedback.startIconAnimation();
            showBottomSheet(new FeedbackBottomSheetDialogFragment(), null);
        });

        binding.buttonLoginAbout.setTooltipText(getString(R.string.title_about));
        binding.buttonLoginAbout.setOnClickListener(v -> {
            if(clickUtil.isDisabled()) return;
            binding.buttonLoginAbout.startIconAnimation();
            startActivity(new Intent(this, AboutActivity.class));
        });

        binding.buttonLoginWebsite.setTooltipText(getString(R.string.info_website));
        binding.buttonLoginWebsite.setOnClickListener(v -> {
            if(clickUtil.isDisabled()) return;
            binding.buttonLoginWebsite.startIconAnimation();
            startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(getString(R.string.url_grocy))));
        });

        if(getIntent().getBooleanExtra(Constants.EXTRA.AFTER_FEATURES_ACTIVITY, false)) {
            showMessage(getString(R.string.msg_features));
        }
    }

    @Override
    protected void onDestroy() {
        super.onDestroy();
        dlHelper.destroy();
    }

    public void requestLogin(String server, String key, boolean checkVersion, boolean isDemo) {
        binding.buttonLoginLogin.setEnabled(false);
        binding.buttonLoginDemo.setEnabled(false);
        dlHelper.get(
                server + "/api/system/info?GROCY-API-KEY=" + key,
                response -> {
                    Log.i(TAG, "requestLogin: " + response);
                    if(!response.contains("grocy_version")) {
                        binding.textInputLoginServer.setError(
                                getString(R.string.error_not_grocy_instance)
                        );
                        binding.buttonLoginLogin.setEnabled(true);
                        binding.buttonLoginDemo.setEnabled(true);
                        openHomeAssistantHelp(server);
                        return;
                    }
                    try {
                        String grocyVersion = new JSONObject(response)
                                .getJSONObject("grocy_version")
                                .getString("Version");
                        ArrayList<String> supportedVersions = new ArrayList<>(
                                Arrays.asList(
                                        getResources().getStringArray(
                                                R.array.compatible_grocy_versions
                                        )
                                )
                        );
                        if(checkVersion && !supportedVersions.contains(grocyVersion)) {
                            Bundle bundle = new Bundle();
                            bundle.putString(Constants.ARGUMENT.SERVER, server);
                            bundle.putString(Constants.ARGUMENT.KEY, key);
                            bundle.putString(Constants.ARGUMENT.VERSION, grocyVersion);
                            bundle.putBoolean(Constants.ARGUMENT.DEMO_CHOSEN, isDemo);
                            bundle.putStringArrayList(
                                    Constants.ARGUMENT.SUPPORTED_VERSIONS,
                                    supportedVersions
                            );
                            showBottomSheet(
                                    new CompatibilityBottomSheetDialogFragment(),
                                    bundle
                            );
                            return;
                        }
                    } catch (JSONException e) {
                        Log.e(TAG, "requestLogin: " + e);
                    }

                    if(DEBUG) Log.i(TAG, "requestLogin: successfully logged in");
                    sharedPrefs.edit()
                            .putString(Constants.PREF.SERVER_URL, server)
                            .putString(Constants.PREF.API_KEY, key)
                            .apply();
                    if(!isDemo) {
                        credentials.edit()
                                .putString(Constants.PREF.SERVER_URL, server)
                                .putString(Constants.PREF.API_KEY, key)
                                .apply();
                    }
                    setResult(Activity.RESULT_OK);
                    loadInfoAndFinish();
                },
                error -> {
                    Log.e(TAG, "requestLogin: VolleyError: " + error);
                    if(error instanceof AuthFailureError) {
                        binding.textInputLoginKey.setError(getString(R.string.error_api_not_working));
                        openHomeAssistantHelp(server);
                    } else if(error instanceof NoConnectionError) {
                        if(error.toString().contains("SSLHandshakeException")) {
                            Bundle bundle = new Bundle();
                            bundle.putString(
                                    Constants.ARGUMENT.TITLE,
                                    getString(R.string.error_handshake)
                            );
                            bundle.putString(
                                    Constants.ARGUMENT.TEXT,
                                    getString(R.string.error_handshake_description, server)
                            );
                            showBottomSheet(new MessageBottomSheetDialogFragment(), bundle);
                        } else if(error.toString().contains("Invalid host")) {
                            binding.textInputLoginServer.setError(
                                    getString(R.string.error_invalid_url)
                            );
                        } else {
                            showMessage(getString(R.string.error_failed_to_connect_to, server));
                        }
                    } else if(error instanceof ServerError && error.networkResponse != null) {
                        int code = error.networkResponse.statusCode;
                        if (code == 404) {
                            binding.textInputLoginServer.setError(
                                    getString(R.string.error_not_grocy_instance)
                            );
                        } else {
                            showMessage(getString(R.string.error_unexpected_response_code, code));
                        }
                    } else if(error instanceof ServerError) {
                        showMessage(getString(R.string.error_unexpected_response));
                    } else if(error instanceof TimeoutError) {
                        showMessage(getString(R.string.error_timeout));
                    } else {
                        showMessage(getString(R.string.error_undefined) + ": " + error);
                    }
                    binding.buttonLoginLogin.setEnabled(true);
                    binding.buttonLoginDemo.setEnabled(true);
                }
        );
    }

    private void loadInfoAndFinish() {
        ConfigUtil.loadInfo(
                new DownloadHelper(this, TAG),
                new GrocyApi(this),
                sharedPrefs,
                this::finish,
                this::finish
        );
    }

    private void openHomeAssistantHelp(String server) {
        if(server.endsWith("_grocy")
                || server.contains("hassio_ingress")
                || server.contains("hassio/ingress")
        ) {
            // maybe a grocy instance on Hass.io - url doesn't work like this
            boolean success = NetUtil.openURL(
                    this,
                    Constants.URL.FAQ + "#user-content-faq4"
            );
            if(!success) {
                Snackbar.make(
                        binding.coordinatorLoginContainer,
                        R.string.error_no_browser,
                        Snackbar.LENGTH_LONG
                ).show();
            }
        }
    }

    public void enableLoginButtons() {
        binding.buttonLoginLogin.setEnabled(true);
        binding.buttonLoginDemo.setEnabled(true);
    }

    private String getServer() {
        Editable server = binding.editTextLoginServer.getText();
        if(server == null) return "";
        return server.toString().replaceAll("/+$", "").trim();
    }

    private String getKey() {
        Editable key = binding.editTextLoginKey.getText();
        if(key == null) return "";
        return key.toString().trim();
    }

    private void showBottomSheet(BottomSheetDialogFragment bottomSheet, Bundle bundle) {
        String tag = bottomSheet.toString();
        Fragment fragment = fragmentManager.findFragmentByTag(tag);
        if (fragment == null || !fragment.isVisible()) {
            if(bundle != null) bottomSheet.setArguments(bundle);
            fragmentManager.beginTransaction().add(bottomSheet, tag).commit();
            if(DEBUG) Log.i(TAG, "showBottomSheet: " + tag);
        } else Log.e(TAG, "showBottomSheet: sheet already visible");
    }

    @Override
    public void onBackPressed() {
        moveTaskToBack(true);
    }

    private void showMessage(String text) {
        Snackbar.make(binding.coordinatorLoginContainer, text, Snackbar.LENGTH_LONG).show();
    }
}
