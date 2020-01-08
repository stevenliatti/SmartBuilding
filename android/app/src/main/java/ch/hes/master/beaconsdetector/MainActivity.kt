package ch.hes.master.beaconsdetector

import android.os.Bundle
import android.view.Menu
import android.view.MenuItem
import android.widget.SeekBar
import android.widget.Switch
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.isVisible
import com.estimote.coresdk.common.config.EstimoteSDK
import com.estimote.coresdk.common.requirements.SystemRequirementsChecker
import com.estimote.coresdk.observation.region.beacon.BeaconRegion
import com.estimote.coresdk.service.BeaconManager
import kotlinx.android.synthetic.main.activity_main.*
import kotlinx.android.synthetic.main.content_main.*
import kotlinx.android.synthetic.main.content_main.view.*
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


    private lateinit var lightSwitch: Switch
    private lateinit var blindSwitch: Switch
    private lateinit var radiatorSwitch: Switch

    private lateinit var lightSeekbar: SeekBar
    private lateinit var blindSeekbar: SeekBar
    private lateinit var radiatorSeekbar: SeekBar

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


        lightSwitch = findViewById(R.id.switch_light)
        blindSwitch = findViewById(R.id.switch_blinds)
        radiatorSwitch = findViewById(R.id.switch_radiators)

        val lightTxt: TextView = findViewById(R.id.txt_light)
        lightSeekbar = findViewById(R.id.seekBar_light)
        val blindTxt: TextView = findViewById(R.id.txt_blinds)
        blindSeekbar = findViewById(R.id.seekBar_blind)
        val radiatorTxt: TextView = findViewById(R.id.txt_radiators)
        radiatorSeekbar = findViewById(R.id.seekbar_radiator)

        val lightPercentTxt: TextView = findViewById(R.id.percentage_light)
        val blindPercentTxt: TextView = findViewById(R.id.percentage_blinds)
        val radiatorPercentTxt: TextView = findViewById(R.id.percentage_radiators)
        lightPercentTxt.text = "0%"
        blindPercentTxt.text = "0%"
        radiatorPercentTxt.text = "0%"

        val temperature_txt: TextView = findViewById(R.id.temperature_txt)
        val humidity_txt: TextView = findViewById(R.id.humidity_txt)
        val luminance_txt: TextView = findViewById(R.id.luminance_txt)



        lightSwitch.setOnClickListener {
            if(lightSwitch.isChecked) {
                val url = "$baseUrl/percentage_dimmers?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=100"
                requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                lightSeekbar.progress = 100
                lightPercentTxt.text = "100%"
            } else {
                val url = "$baseUrl/percentage_dimmers?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=0"
                requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                lightSeekbar.progress = 0
                lightPercentTxt.text = "0%"
            }
        }

        blindSwitch.setOnClickListener {
            if(blindSwitch.isChecked) {
                val url = "$baseUrl/open_blinds?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}"
                requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                blindSeekbar.progress = 100
                blindPercentTxt.text = "100%"
            } else {
                val url = "$baseUrl/close_blinds?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}"
                requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                blindSeekbar.progress = 0
                blindPercentTxt.text = "0%"
            }
        }

        radiatorSwitch.setOnClickListener {
            if(radiatorSwitch.isChecked) {
                val url = "$baseUrl/percentage_radiator?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=100"
                requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                radiatorSeekbar.progress = 100
                radiatorPercentTxt.text = "100%"
            } else {
                val url = "$baseUrl/percentage_radiator?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=1"
                requestController.httpGet(url, this, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                radiatorSeekbar.progress = 0
                radiatorPercentTxt.text = "0%"
            }
        }

        lightSeekbar.setOnSeekBarChangeListener (object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {}
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}

            override fun onStopTrackingTouch(seek: SeekBar) {
                val url = "$baseUrl/percentage_dimmers?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=${seek.progress}"
                requestController.httpGet(url, seek.context, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                lightPercentTxt.text = seek.progress.toString() + '%'
                lightSwitch.isChecked = true
                if (seek.progress == 0) {
                    lightSwitch.isChecked = false
                }
            }

        })

        blindSeekbar.setOnSeekBarChangeListener (object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {}
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}

            override fun onStopTrackingTouch(seek: SeekBar) {
                val url = "$baseUrl/percentage_blinds?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=${seek.progress}"
                requestController.httpGet(url, seek.context, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                blindPercentTxt.text = seek.progress.toString() + '%'
                blindSwitch.isChecked = true
                if (seek.progress == 0) {
                    blindSwitch.isChecked = false
                }
            }
        })

        radiatorSeekbar.setOnSeekBarChangeListener (object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {}
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}

            override fun onStopTrackingTouch(seek: SeekBar) {
                val url = "$baseUrl/percentage_radiator?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}&percentage=${seek.progress}"
                requestController.httpGet(url, seek.context, object : ServerCallback<JSONObject> {
                    override fun onSuccess(result: JSONObject) {
                        println(result)
                    }
                })
                radiatorPercentTxt.text = seek.progress.toString() + '%'
                radiatorSwitch.isChecked = true
                if (seek.progress == 0) {
                    radiatorSwitch.isChecked = false
                }
            }
        })



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

                    requestController.httpGet("$baseUrl/get_devices?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            val devices = result.getJSONArray("devices")
                            lightSwitch.isVisible = false
                            lightSeekbar.isVisible = false
                            lightTxt.isVisible = false
                            lightPercentTxt.isVisible = false
                            blindSwitch.isVisible = false
                            blindSeekbar.isVisible = false
                            blindTxt.isVisible = false
                            blindPercentTxt.isVisible = false
                            radiatorSwitch.isVisible = false
                            radiatorSeekbar.isVisible = false
                            radiatorTxt.isVisible = false
                            radiatorPercentTxt.isVisible = false

                            for (i in 0 until devices.length()) {
                                val jsObj = devices.getJSONObject(i)

                                when {
                                    jsObj.getString("name") == "blind" -> {
                                        blindSwitch.isVisible = true
                                        blindSeekbar.isVisible = true
                                        blindTxt.isVisible = true
                                        blindPercentTxt.isVisible = true
                                    }
                                    jsObj.getString("name") == "radiator" -> {
                                        radiatorSwitch.isVisible = true
                                        radiatorSeekbar.isVisible = true
                                        radiatorTxt.isVisible = true
                                        radiatorPercentTxt.isVisible = true
                                    }
                                    jsObj.getString("name") == "ZE27" -> {
                                        lightSwitch.isVisible = true
                                        lightSeekbar.isVisible = true
                                        lightTxt.isVisible = true
                                        lightPercentTxt.isVisible = true
                                    }
                                }
                            }
                        }
                    })


                    requestController.httpGet("$baseUrl/avg_temperature?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                val avg_temperature = result.getInt("avg_temperature")
                                temperature_txt.text = avg_temperature.toString() + "° celsius"
                            }
                            catch (e: JSONException) {
                                println("avg_temperature: value not found ($e)")
                            }
                        }
                    })

                    requestController.httpGet("$baseUrl/avg_humidity?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                val avg_humidity = result.getInt("avg_humidity")
                                humidity_txt.text = avg_humidity.toString() + "%"
                            }
                            catch (e: JSONException) {
                                println("avg_humidity: value not found ($e)")
                            }
                        }
                    })

                    requestController.httpGet("$baseUrl/avg_luminance?uuid=${actualBeacon.uuid}&major=${actualBeacon.major}&minor=${actualBeacon.minor}", this, object : ServerCallback<JSONObject> {
                        override fun onSuccess(result: JSONObject) {
                            try {
                                val avg_luminance = result.getInt("avg_luminance")
                                luminance_txt.text = avg_luminance.toString() + " lumen"
                            }
                            catch (e: JSONException) {
                                println("avg_luminance: value not found ($e)")
                            }
                        }
                    })
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
