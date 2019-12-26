package ch.hes.master.beaconsdetector

import android.content.Context
import android.util.Log
import com.android.volley.Request
import com.android.volley.RequestQueue
import com.android.volley.Response
import com.android.volley.toolbox.JsonObjectRequest
import com.android.volley.toolbox.Volley
import org.json.JSONObject

interface ServerCallback<T> {
    fun onSuccess(result: T)
}

class VolleyRequestController {
    fun httpGet(URL: String, context: Context, callback: ServerCallback<JSONObject>) {
        val jsonObjReq = JsonObjectRequest(Request.Method.GET, URL, null,
            Response.Listener { response ->
                callback.onSuccess(response) // call call back function here
            },
            Response.ErrorListener { error ->
                Log.println(Log.DEBUG, this.javaClass.name, "error in httpGet : $error,\n$URL\n$callback")
            })

        // Adding request to request queue
        HttpQueue.getInstance(context).addToRequestQueue(jsonObjReq)
    }

    fun httpPost(URL: String, jsonData: JSONObject, context: Context, callback: ServerCallback<JSONObject>) {
        val jsonObjReq = JsonObjectRequest(Request.Method.POST, URL, jsonData,
            Response.Listener { response ->
                callback.onSuccess(response) // call call back function here
            },
            Response.ErrorListener { error ->
                Log.println(Log.DEBUG, this.javaClass.name, "error in httpPost : $error,\n$URL\n$jsonData\n$callback")
            })

        // Adding request to request queue
        HttpQueue.getInstance(context).addToRequestQueue(jsonObjReq)
    }

}


class HttpQueue constructor(context: Context) {
    companion object {
        @Volatile
        private var INSTANCE: HttpQueue? = null
        fun getInstance(context: Context) =
            INSTANCE ?: synchronized(this) {
                INSTANCE ?: HttpQueue(context).also {
                    INSTANCE = it
                }
            }
    }

    private val requestQueue: RequestQueue by lazy {
        // applicationContext is key, it keeps you from leaking the
        // Activity or BroadcastReceiver if someone passes one in.
        Volley.newRequestQueue(context.applicationContext)
    }

    fun <T> addToRequestQueue(req: Request<T>) {
        requestQueue.add(req)
    }
}