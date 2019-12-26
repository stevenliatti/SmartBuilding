package ch.hes.master.beaconsdetector

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.view.View
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import com.estimote.coresdk.common.config.EstimoteSDK
import com.estimote.coresdk.common.requirements.SystemRequirementsChecker
import com.estimote.coresdk.observation.region.beacon.BeaconRegion
import com.estimote.coresdk.service.BeaconManager
import kotlinx.android.synthetic.main.activity_main.*
import java.util.*
import kotlin.collections.HashMap


class MainActivity : AppCompatActivity() {

    private lateinit var beaconsRooms: Map<Int, Int>

    private lateinit var requestController: VolleyRequestController
    private lateinit var roomTextView: TextView
    private lateinit var lightButton: Button
    private lateinit var blindButton: Button

    private lateinit var beaconManager: BeaconManager
    private lateinit var region: BeaconRegion

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.content_main)
        setSupportActionBar(toolbar)

        beaconsRooms = HashMap()
        requestController = VolleyRequestController()

        roomTextView = findViewById(R.id.room_text_view)
        lightButton = findViewById(R.id.light_button)
        blindButton = findViewById(R.id.blind_button)

        EstimoteSDK.initialize(applicationContext, "", "")
        EstimoteSDK.enableDebugLogging(true)

        beaconManager = BeaconManager(this)
        region = BeaconRegion(
            "rooms",
            UUID.fromString("b9407f30-f5f8-466e-aff9-25556b57fe6d"),
            17644, null
        )

        beaconManager.setRangingListener(BeaconManager.BeaconRangingListener { region, list ->
            if (list.isNotEmpty()) {
                println("region: $region, list: $list")
                val nearestBeacon = list[0]

                if (beaconsRooms.containsKey(nearestBeacon.minor)) {
                    roomTextView.text = "Room ${beaconsRooms[nearestBeacon.minor]}"
                }
                else {
                    // TODO: get real info
                    roomTextView.text = "Room ${nearestBeacon.minor}"
//                    requestController.httpGet("asdf", applicationContext, object : ServerCallback<JSONObject> {
//                        override fun onSuccess(result: JSONObject) {
//                            roomTextView.text = "Room $result"
//                            (beaconsRooms as HashMap<Int, Int>)[nearestBeacon.minor] = result.getInt("number")
//                        }
//                    })
                }

                lightButton.visibility = View.VISIBLE
                blindButton.visibility = View.VISIBLE

            }
        })

    }

    override fun onResume() {
        super.onResume()
        SystemRequirementsChecker.checkWithDefaultDialogs(this)
        beaconManager.connect { beaconManager.startRanging(region) }
    }


    override fun onPause() {
        beaconManager.stopRanging(region)
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
