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
import org.json.JSONException
import org.json.JSONObject
import java.util.*
import kotlin.collections.HashMap


data class Beacon(val uuid: String, val major: Int, val minor: Int, val roomNumber: Int)

class MainActivity : AppCompatActivity() {

    private val baseUrl = "http://iot.liatti.ch"

    private lateinit var beaconsMap: MutableMap<Int, Beacon>
    private lateinit var actualBeacon: Beacon

    private lateinit var requestController: VolleyRequestController

    private lateinit var roomTextView: TextView

    private lateinit var readPercentageBlindsView: TextView
    private lateinit var sensorGetTemperatureView: TextView
    private lateinit var sensorGetHumidityView: TextView
    private lateinit var sensorGetLuminanceView: TextView
    private lateinit var sensorGetMotionView: TextView
    private lateinit var dimmerGetLevelView: TextView

    private lateinit var lightOnButton: Button
    private lateinit var lightOffButton: Button
    private lateinit var openBlindButton: Button
    private lateinit var closeBlindButton: Button
    private lateinit var openRadiatorButton: Button
    private lateinit var closeRadiatorButton: Button

    private lateinit var beaconManager: BeaconManager
    private lateinit var region: BeaconRegion

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.content_main)
        setSupportActionBar(toolbar)

        requestController = VolleyRequestController()
        beaconsMap = HashMap()

        requestController.httpGet("$baseUrl/get_beacons", this, object : ServerCallback<JSONObject> {
            override fun onSuccess(result: JSONObject) {
                val beacons = result.getJSONArray("beacons")
                for (i in 0 until beacons.length()) {
                    val br = beacons.getJSONObject(i)
                    val beacon = Beacon(br.getString("uuid"), br.getInt("major"),
                        br.getInt("minor"), br.getInt("room_number"))
                    beaconsMap[br.getInt("minor")] = beacon
                }
            }

        })

        roomTextView = findViewById(R.id.room_text_view)

        readPercentageBlindsView = findViewById(R.id.read_percentage_blinds)
        sensorGetTemperatureView = findViewById(R.id.sensor_get_temperature)
        sensorGetHumidityView = findViewById(R.id.sensor_get_humidity)
        sensorGetLuminanceView = findViewById(R.id.sensor_get_luminance)
        sensorGetMotionView = findViewById(R.id.sensor_get_motion)
        dimmerGetLevelView = findViewById(R.id.dimmer_get_level)

        lightOnButton = findViewById(R.id.light_button_on)
        lightOffButton = findViewById(R.id.light_button_off)
        openBlindButton = findViewById(R.id.open_blind_button)
        closeBlindButton = findViewById(R.id.close_blind_button)
        openRadiatorButton = findViewById(R.id.open_radiator_button)
        closeRadiatorButton = findViewById(R.id.close_radiator_button)

        lightOnButton.setOnClickListener {
            val url = "$baseUrl/percentage_dimmers?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=100"
            requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                override fun onSuccess(result: JSONObject) {
                    println(result)
                }
            })
        }
        lightOffButton.setOnClickListener {
            val url = "$baseUrl/percentage_dimmers?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=0"
            requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                override fun onSuccess(result: JSONObject) {
                    println(result)
                }
            })
        }
        openBlindButton.setOnClickListener {
            val url = "$baseUrl/open_blinds?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}"
            requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                override fun onSuccess(result: JSONObject) {
                    println(result)
                }
            })
        }
        closeBlindButton.setOnClickListener {
            val url = "$baseUrl/close_blinds?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}"
            requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                override fun onSuccess(result: JSONObject) {
                    println(result)
                }
            })
        }
        openRadiatorButton.setOnClickListener {
            val url = "$baseUrl/percentage_radiator?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=100"
            requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                override fun onSuccess(result: JSONObject) {
                    println(result)
                }
            })
        }
        closeRadiatorButton.setOnClickListener {
            val url = "$baseUrl/percentage_radiator?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=1"
            requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                override fun onSuccess(result: JSONObject) {
                    println(result)
                }
            })
        }

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

                if (beaconsMap.containsKey(nearestBeacon.minor)) {
                    actualBeacon = beaconsMap[nearestBeacon.minor]!!
                    roomTextView.text = "Room ${beaconsMap[nearestBeacon.minor]?.roomNumber}"

                    requestController.httpGet("$baseUrl/read_percentage_blinds?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                readPercentageBlindsView.text = "Percentage blinds: ${result.getInt("value")}"
                            }
                            catch (e: JSONException) {
                                println("read_percentage_blinds: value not found ($e)")
                            }
                        }
                    })
                    requestController.httpGet("$baseUrl/sensor_get_temperature?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                sensorGetTemperatureView.text = "Temperature: ${result.getInt("value")}"
                            }
                            catch (e: JSONException) {
                                println("sensor_get_temperature: value not found ($e)")
                            }
                        }
                    })
                    requestController.httpGet("$baseUrl/sensor_get_humidity?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                sensorGetHumidityView.text = "Humidity: ${result.getInt("value")}"
                            }
                            catch (e: JSONException) {
                                println("sensor_get_humidity: value not found ($e)")
                            }
                        }
                    })
                    requestController.httpGet("$baseUrl/sensor_get_luminance?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                sensorGetLuminanceView.text = "Luminance: ${result.getInt("value")}"
                            }
                            catch (e: JSONException) {
                                println("sensor_get_luminance: value not found ($e)")
                            }
                        }
                    })
                    requestController.httpGet("$baseUrl/sensor_get_motion?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                sensorGetMotionView.text = "Presence: ${result.getInt("value")}"
                            }
                            catch (e: JSONException) {
                                println("sensor_get_motion: value not found ($e)")
                            }
                        }
                    })
                    requestController.httpGet("$baseUrl/dimmer_get_level?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                dimmerGetLevelView.text = "Dimmer level: ${result.getInt("value")}"
                            }
                            catch (e: JSONException) {
                                println("dimmer_get_level: value not found ($e)")
                            }
                        }
                    })

                    lightOnButton.visibility = View.VISIBLE
                    lightOffButton.visibility = View.VISIBLE
                    openBlindButton.visibility = View.VISIBLE
                    closeBlindButton.visibility = View.VISIBLE
                    openRadiatorButton.visibility = View.VISIBLE
                    closeRadiatorButton.visibility = View.VISIBLE
                }

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
