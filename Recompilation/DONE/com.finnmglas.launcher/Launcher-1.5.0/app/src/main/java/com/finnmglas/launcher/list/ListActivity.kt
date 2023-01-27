package com.finnmglas.launcher.list

import android.app.Activity
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.viewpager.widget.ViewPager
import com.finnmglas.launcher.*
import com.finnmglas.launcher.settings.intendedSettingsPause
import com.google.android.material.tabs.TabLayout
import kotlinx.android.synthetic.main.list.*
import android.content.Context
import androidx.fragment.app.Fragment
import androidx.fragment.app.FragmentManager
import androidx.fragment.app.FragmentPagerAdapter
import com.finnmglas.launcher.list.apps.ListFragmentApps
import com.finnmglas.launcher.list.other.ListFragmentOther

var intendedChoosePause = false // know when to close

// TODO: Better solution for this intercommunication fuctionality (used in list-fragments)
var intention = "view"
var forApp = ""

/**
 * The [ListActivity] is the most general purpose activity in Launcher:
 * - used to view all apps and edit their settings
 * - used to choose an app / intent to be launched
 *
 * The activity itself can also be chosen to be launched as an action.
 */
class ListActivity : AppCompatActivity(), UIObject {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Initialise layout
        setContentView(R.layout.list)
    }

    override fun onStart(){
        super<AppCompatActivity>.onStart()
        super<UIObject>.onStart()
    }

    override fun onPause() {
        super.onPause()
        intendedSettingsPause = false
        if(!intendedChoosePause) finish()
    }

    override fun onResume() {
        super.onResume()
        intendedChoosePause = false
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_UNINSTALL) {
            if (resultCode == Activity.RESULT_OK) {
                Toast.makeText(this, getString(R.string.list_removed), Toast.LENGTH_LONG).show()
                finish()
            } else if (resultCode == Activity.RESULT_FIRST_USER) {
                Toast.makeText(this, getString(R.string.list_not_removed), Toast.LENGTH_LONG).show()
                finish()
            }
        }
    }

    override fun applyTheme() {
        list_container.setBackgroundColor(dominantColor)
        list_appbar.setBackgroundColor(dominantColor)
        list_close.setTextColor(vibrantColor)

        list_tabs.setSelectedTabIndicatorColor(vibrantColor)
    }

    override fun setOnClicks() {
        list_close.setOnClickListener() { finish() }
    }

    override fun adjustLayout() {
        // get info about which action this activity is open for
        val bundle = intent.extras
        if (bundle != null) {
            intention = bundle.getString("intention")!! // why choose an app
            if (intention != "view")
                forApp = bundle.getString("forApp")!! // which app we choose
        }

        // Hide tabs for the "view" action
        if (intention == "view") {
            list_tabs.visibility = View.GONE
        }

        when (intention) {
            "view" -> list_heading.text = getString(R.string.list_title_view)
            "pick" -> list_heading.text = getString(R.string.list_title_pick)
        }

        val sectionsPagerAdapter = ListSectionsPagerAdapter(this, supportFragmentManager)
        val viewPager: ViewPager = findViewById(R.id.list_viewpager)
        viewPager.adapter = sectionsPagerAdapter
        val tabs: TabLayout = findViewById(R.id.list_tabs)
        tabs.setupWithViewPager(viewPager)
    }
}

private val TAB_TITLES = arrayOf(
    R.string.list_tab_app,
    R.string.list_tab_other
)

/**
 * The [ListSectionsPagerAdapter] returns the fragment,
 * which corresponds to the selected tab in [ListActivity].
 */
class ListSectionsPagerAdapter(private val context: Context, fm: FragmentManager)
    : FragmentPagerAdapter(fm, BEHAVIOR_RESUME_ONLY_CURRENT_FRAGMENT) {

    override fun getItem(position: Int): Fragment {
        return when (position){
            0 -> ListFragmentApps()
            1 -> ListFragmentOther()
            else -> Fragment()
        }
    }

    override fun getPageTitle(position: Int): CharSequence? {
        return context.resources.getString(TAB_TITLES[position])
    }

    override fun getCount(): Int {
        return when (intention) {
            "view" -> 1
            else -> 2
        }
    }
}