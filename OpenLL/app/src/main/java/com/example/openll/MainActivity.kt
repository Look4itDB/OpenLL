package com.example.openll

import android.Manifest
import android.content.pm.PackageManager
import android.location.Location
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.example.openll.ui.theme.OpenLLTheme
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import kotlinx.coroutines.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.*

class MainActivity : ComponentActivity() {
    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private var locationJob: Job? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)

        setContent {
            OpenLLTheme {
                MainScreen { url, isAutoSending, interval, showSnackbar, addToHistory, manualTrigger ->
                    if (manualTrigger) {
                        sendLocation(url, showSnackbar, addToHistory)
                    } else if (isAutoSending) {
                        startAutoLocationUpdates(url, interval, showSnackbar, addToHistory)
                    } else {
                        stopAutoLocationUpdates()
                    }
                }
            }
        }
    }

    private fun startAutoLocationUpdates(url: String, interval: Int, showSnackbar: (String) -> Unit, addToHistory: (String) -> Unit) {
        stopAutoLocationUpdates() // Stop previous job if running

        locationJob = CoroutineScope(Dispatchers.IO).launch {
            while (isActive) {
                sendLocation(url, showSnackbar, addToHistory)
                delay(interval * 1000L) // Interval in seconds
            }
        }
    }

    private fun stopAutoLocationUpdates() {
        locationJob?.cancel()
    }

    private fun sendLocation(url: String, showSnackbar: (String) -> Unit, addToHistory: (String) -> Unit) {
        Log.d("DEBUG", "Checking location permission...")
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) == PackageManager.PERMISSION_GRANTED) {
            Log.d("DEBUG", "Permission granted, getting location...")

            fusedLocationClient.lastLocation.addOnSuccessListener { location: Location? ->
                if (location != null) {
                    Log.d("DEBUG", "Location retrieved: Lat=${location.latitude}, Lon=${location.longitude}")
                    postLocation(url, location.latitude, location.longitude, showSnackbar, addToHistory)
                } else {
                    Log.e("ERROR", "Failed to get location")
                    showSnackbar("Failed to get location")
                    addToHistory("Failed to get location")
                }
            }
        } else {
            Log.w("WARNING", "Location permission not granted, requesting permission...")
            requestPermissions.launch(Manifest.permission.ACCESS_FINE_LOCATION)
        }
    }

    private val requestPermissions =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { isGranted: Boolean ->
            if (isGranted) {
                Log.d("DEBUG", "Permission granted, retrying location request...")
            } else {
                Log.e("ERROR", "Permission denied")
            }
        }

    private fun postLocation(url: String, latitude: Double, longitude: Double, showSnackbar: (String) -> Unit, addToHistory: (String) -> Unit) {
        CoroutineScope(Dispatchers.IO).launch {
            val client = OkHttpClient()

            val json = JSONObject().apply {
                put("device_id", "047")
                put("coordinates", JSONArray().apply {
                    put(JSONObject().apply {
                        put("latitude", latitude)
                        put("longitude", longitude)
                    })
                })
            }

            val requestBody = json.toString().toRequestBody("application/json".toMediaTypeOrNull())

            val request = Request.Builder()
                .url(url)
                .post(requestBody)
                .addHeader("Content-Type", "application/json")
                .build()

            Log.d("DEBUG", "Sending POST request to: $url")
            Log.d("DEBUG", "Request Body: $json")

            try {
                val response = client.newCall(request).execute()
                val responseBody = response.body?.string()
                Log.d("DEBUG", "Server Response: $responseBody")

                val timestamp = SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())
                val responseText = "[$timestamp] ${responseBody ?: "No Response"}"

                withContext(Dispatchers.Main) {
                    showSnackbar(responseText)
                    addToHistory(responseText)
                }
            } catch (e: Exception) {
                Log.e("ERROR", "Request failed: ${e.message}")
                val errorText = "[${SimpleDateFormat("HH:mm:ss", Locale.getDefault()).format(Date())}] Request failed: ${e.message}"

                withContext(Dispatchers.Main) {
                    showSnackbar(errorText)
                    addToHistory(errorText)
                }
            }
        }
    }
}

@Composable
fun MainScreen(onSendClick: (String, Boolean, Int, (String) -> Unit, (String) -> Unit, Boolean) -> Unit) {
    var url by remember { mutableStateOf("https://57a0-61-1-175-163.ngrok-free.app/push_location") }
    var isAutoSending by remember { mutableStateOf(false) }
    var interval by remember { mutableStateOf(3) } // Default interval
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    // List of responses
    var responses by remember { mutableStateOf(listOf<String>()) }

    fun showSnackbar(message: String) {
        coroutineScope.launch {
            snackbarHostState.showSnackbar(message)
        }
    }

    fun addToHistory(message: String) {
        responses = listOf(message) + responses.take(9) // Store last 10 responses
    }

    Scaffold(
        snackbarHost = { SnackbarHost(snackbarHostState) }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
                .padding(paddingValues),
            verticalArrangement = Arrangement.Top
        ) {
            OutlinedTextField(
                value = url,
                onValueChange = { url = it },
                label = { Text("Enter Server URL") },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(16.dp))

            Text("Select Interval: $interval seconds")
            Slider(
                value = interval.toFloat(),
                onValueChange = { interval = it.toInt() },
                valueRange = 1f..2f, // Allow 1-10 seconds
                steps = 100
            )

            Spacer(modifier = Modifier.height(16.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text("Auto Send Location")
                Switch(
                    checked = isAutoSending,
                    onCheckedChange = {
                        isAutoSending = it
                        onSendClick(url, isAutoSending, interval, ::showSnackbar, ::addToHistory, false)
                    }
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { onSendClick(url, false, interval, ::showSnackbar, ::addToHistory, true) },
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("Send Location Once")
            }

            LazyColumn {
                items(responses) { response ->
                    Text(response, modifier = Modifier.padding(8.dp))
                }
            }
        }
    }
}
