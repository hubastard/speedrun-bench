// Kotlin is built in since the Android Gradle plugin 9; the Compose compiler is a Kotlin plugin.
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.plugin.compose")
}

// The Compose libraries' version: ./gradlew -Pbom=2025.06.00 ... builds with older ones.
val bom = (findProperty("bom") as String?) ?: "2026.05.01"

android {
    namespace = "dev.speedrun.composebench"
    compileSdk = 36

    defaultConfig {
        applicationId = "dev.speedrun.composebench"
        minSdk = 26
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        // A release build, as apps ship, signed with the debug key so that it installs.
        release {
            signingConfig = signingConfigs.getByName("debug")
        }
    }

    buildFeatures { compose = true }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:$bom"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.activity:activity-compose:1.9.3")
}
