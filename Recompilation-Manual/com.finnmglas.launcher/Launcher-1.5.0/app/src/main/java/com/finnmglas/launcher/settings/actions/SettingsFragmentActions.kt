package com.finnmglas.launcher.settings.actions

import android.content.ActivityNotFoundException
import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import com.finnmglas.launcher.*
import com.finnmglas.launcher.list.ListActivity
import com.finnmglas.launcher.settings.intendedSettingsPause
import kotlinx.android.synthetic.main.settings_actions.*


/**
 *  The [SettingsFragmentActions] is a used as a tab in the SettingsActivity.
 *
 *  It is used to change Apps / Intents to be launched when a specific action
 *  is triggered.
 *  It also allows the user to view all apps ([ListActivity]) or install new ones.
 */

class SettingsFragmentActions : Fragment(), UIObject {

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.settings_actions, container, false)
    }

    override fun onStart() {
        super<Fragment>.onStart()
        super<UIObject>.onStart()
    }

    override fun applyTheme() {
        settings_actions_container.setBackgroundColor(dominantColor)

        setButtonColor(settings_actions_button_view_apps, vibrantColor)
        setButtonColor(settings_actions_button_install_apps, vibrantColor)
    }

    override fun setOnClicks() {

        // App management buttons
        settings_actions_button_view_apps.setOnClickListener{
            val intent = Intent(this.context, ListActivity::class.java)
            intent.putExtra("intention", "view")
            intendedSettingsPause = true
            startActivity(intent)
        }
        settings_actions_button_install_apps.setOnClickListener{
            try {
                val rateIntent = Intent(
                    Intent.ACTION_VIEW,
                    Uri.parse("https://play.google.com/store/apps/"))
                startActivity(rateIntent)
                intendedSettingsPause = true
            } catch (e: ActivityNotFoundException) {
                Toast.makeText(this.context, getString(R.string.settings_apps_toast_store_not_found), Toast.LENGTH_SHORT)
                    .show()
            }
        }
    }
}