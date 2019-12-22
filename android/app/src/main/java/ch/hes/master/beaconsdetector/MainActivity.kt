package ch.hes.master.beaconsdetector

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.estimote.coresdk.common.config.EstimoteSDK
import com.estimote.coresdk.common.requirements.SystemRequirementsChecker
import com.estimote.coresdk.observation.region.beacon.BeaconRegion
import com.estimote.coresdk.service.BeaconManager
import com.google.android.material.snackbar.Snackbar
import kotlinx.android.synthetic.main.activity_main.*
import java.util.*


class MainActivity : AppCompatActivity() {

    private lateinit var roomTextView: TextView

    private var beaconManager: BeaconManager? = null
    private var region: BeaconRegion? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        setSupportActionBar(toolbar)

        fab.setOnClickListener { view ->
            Snackbar.make(view, "Replace with your own action", Snackbar.LENGTH_LONG)
                .setAction("Action", null).show()
        }

        roomTextView = findViewById(R.id.room_text_view)

        EstimoteSDK.initialize(applicationContext, "", "")
        EstimoteSDK.enableDebugLogging(true)

        beaconManager = BeaconManager(this)
        region = BeaconRegion(
            "rooms",
            UUID.fromString("b9407f30-f5f8-466e-aff9-25556b57fe6d"),
            17644, null
        )

        beaconManager!!.setRangingListener(BeaconManager.BeaconRangingListener { region, list ->
            if (list.isNotEmpty()) {
                println("region: $region, list: $list")
                roomTextView.text = list[0].minor.toString()
            }
        })

    }

    override fun onResume() {
        super.onResume()
        SystemRequirementsChecker.checkWithDefaultDialogs(this)
        beaconManager!!.connect { beaconManager!!.startRanging(region) }
    }


    override fun onPause() {
        beaconManager!!.stopRanging(region)
        super.onPause()
    }




    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        // Inflate the menu; this adds items to the action bar if it is present.
        menuInflater.inflate(R.menu.menu_main, menu)
        return true
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return when (item.itemId) {
            R.id.action_settings -> true
            else -> super.onOptionsItemSelected(item)
        }
    }
}
