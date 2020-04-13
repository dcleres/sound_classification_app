# Android Basics

## Bootcamp information

### File System in Android

- The `AndroidManifest.xml` file describes all of the components of your Android app. ==All components for an app, such as each `Activity`, must be declared in this XML file.==
- The **res** folder holds resources, such as layouts, strings, and images. An `Activity` is usually associated with a layout of UI views defined as an XML file. This file is usually named after its `Activity`. For instance for the MainActivity we have a main_activity.xml file.
- The **java** folder includes Java class files in three subfolders, as shown in the figure above. The **com.example.soundclassificationapp** (or the domain name you have specified) folder contains all the files for an app package. The other two folders are used for **testing** and described in another lesson. For the Hello World app, there is only one package and it contains `MainActivity.java`. The name of the first `Activity` (screen) the user sees, which also initializes app-wide resources, is customarily called **MainActivity** (the file extension is omitted in the **Project > Android** pane).
- The Gradle build system in Android Studio makes it easy to include external binaries or other library modules to your build as dependencies.
  - Look for the **build.gradle(Project: HelloWorld)** file: This is where you'll find the configuration options that are common to all of the modules that make up your project. Every Android Studio project contains a single, top-level Gradle build file. Most of the time, you won't need to make any changes to this file, but it's still useful to understand its contents. By default, the top-level build file uses the `buildscript` block to define the Gradle repositories and dependencies that are common to all modules in the project. 
  - In addition to the project-level `build.gradle` file, each module has a `build.gradle` file of its own, which allows you to configure build settings for each specific module (the HelloWorld app has only one module). Configuring these build settings allows you to provide custom packaging options, such as additional build types and product flavors. You can also override settings in the `AndroidManifest.xml` file or the top-level `build.gradle` file. This file is most often the file to edit when changing app-level configurations, such as declaring dependencies in the `dependencies` section. You can declare a library dependency using one of several different dependency configurations. Each dependency configuration provides Gradle different instructions about how to use the library. For example, the statement `implementation fileTree(dir: 'libs', include: ['*.jar'])` adds a dependency of all ".jar" files inside the `libs` directory.

### Virtual Devices

- Android Studio, select **Tools > Android > AVD Manager**, or click the AVD Manager icon ![AVD Manager Icon](https://codelabs.developers.google.com/codelabs/android-training-hello-world/img/c46555f7a03d86c.png) in the toolbar. The **Your Virtual Devices** screen appears. If you've already created virtual devices, the screen shows them (as shown in the figure below); otherwise you see a blank list.

### Physical Devices

- 4.1 Turn on USB debugging

To let Android Studio communicate with your device, you must turn on USB Debugging on your Android device. This is enabled in the **Developer options** settings of your device.

On Android 4.2 and higher, the **Developer options** screen is hidden by default. To show developer options and enable USB Debugging:

1. On your device, open **Settings**, search for **About phone**, click on **About phone**, and tap **Build number** seven times.
2. Return to the previous screen (**Settings / System**). **Developer options** appears in the list. Tap **Developer options**.
3. Choose **USB Debugging**.

- Run your app on a device

Now you can connect your device and run the app from Android Studio.

1. Connect your device to your development machine with a USB cable.
2. Click the **Run** button ![Android Studio Run icon](https://codelabs.developers.google.com/codelabs/android-training-hello-world/img/609c3e4473493202.png) in the toolbar. The **Select Deployment Target** window opens with the list of available emulators and connected devices.
3. Select your device, and click **OK**.

Android Studio installs and runs the app on your device.

- Troubleshooting

If your Android Studio does not recognize your device, try the following:

1. Unplug and replug your device.
2. Restart Android Studio.

If your computer still does not find the device or declares it "unauthorized", follow these steps:

1. Unplug the device.
2. On the device, open **Developer Options in Settings app**.
3. Tap Revoke **USB Debugging** authorizations.
4. Reconnect the device to your computer.
5. When prompted, grant authorizations.

### Debug the app

In this task, you will add [`Log`](https://developer.android.com/reference/android/util/Log.html) statements to your app, which display messages in the **Logcat** pane. `Log` messages are a powerful debugging tool that you can use to check on values, execution paths, and report exceptions.

1. the **Logcat** tab for opening and closing the **Logcat** pane, which displays information about your app as it is running. If you add `Log` statements to your app, `Log` messages appear here.
2. The `Log` level menu set to **Verbose** (the default), which shows all `Log` messages. Other settings include **Debug**, **Error**, **Info**, and **Warn**.

3.  Add log statements to your app:

`Log` statements in your app code display messages in the Logcat pane. For example:

```
Log.d("MainActivity", "Hello World"); 
```

The parts of the message are:

- `Log`: The [`Log`](http://developer.android.com/reference/android/util/Log.html) class for sending log messages to the Logcat pane.
- `d`: The **Debug** `Log` level setting to filter log message display in the Logcat pane. Other log levels are `e` for **Error**, `w` for **Warn**, and `i` for **Info**.
- `"MainActivity"`: The first argument is a tag which can be used to filter messages in the Logcat pane. This is commonly the name of the `Activity` from which the message originates. However, you can make this anything that is useful to you for debugging.

By convention, log tags are defined as constants for the `Activity`:

```
private static final String LOG_TAG = MainActivity.class.getSimpleName(); 
```

- `"Hello world"`: The second argument is the actual message.

Follow these steps:

1. Open your Hello World app in Android studio, and open `MainActivity`.
2. To add unambiguous imports automatically to your project (such as `android.util.Log` required for using `Log`), choose **File > Settings** in Windows, or **Android Studio > Preferences** in macOS.
3. Choose **Editor > General >Auto Import**. Select all checkboxes and set **Insert imports on paste** to **All**.
4. Click **Apply** and then click **OK**.
5. In the `onCreate()` method of `MainActivity`, add the following statement:

```
Log.d("MainActivity", "Hello World"); 
```

The `onCreate()` method should now look like the following code:

```
@Override
protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_main);
    Log.d("MainActivity", "Hello World");
}
```

1. If the Logcat pane is not already open, click the **Logcat** tab at the bottom of Android Studio to open it.
2. Check that the name of the target and package name of the app are correct.
3. Change the `Log` level in the **Logcat** pane to **Debug** (or leave as **Verbose** since there are so few log messages).
4. Run your app.

The following message should appear in the Logcat pane:

```
11-24 14:06:59.001 4696-4696/? D/MainActivity: Hello World
```

## Bootcamp summary

- To install Android Studio, go to [Android Studio](https://developer.android.com/sdk/index.html) and follow the instructions to download and install it.
- When creating a new app, ensure that **API 15: Android 4.0.3 IceCreamSandwich** is set as the Minimum SDK.
- To see the app's Android hierarchy in the Project pane, click the **Project** tab in the vertical tab column, and then choose **Android** in the popup menu at the top.
- Edit the `build.gradle(Module:app)` file when you need to add new libraries to your project or change library versions.
- All code and resources for the app are located within the `app` and `res` folders. The `java` folder includes activities, tests, and other components in Java source code. The `res` folder holds resources, such as layouts, strings, and images.
- Edit the `AndroidManifest.xml` file to add features components and permissions to your Android app. All components for an app, such as multiple activities, must be declared in this XML file.
- Use the [Android Virtual Device (AVD) manager](http://developer.android.com/tools/devices/managing-avds.html) to create a virtual device (also known as an emulator) to run your app.
- Add [`Log`](https://developer.android.com/reference/android/util/Log.html) statements to your app, which display messages in the Logcat pane as a basic tool for debugging.
- To run your app on a physical Android device using Android Studio, turn on USB Debugging on the device. Open **Settings > About phone** and tap **Build number** seven times. Return to the previous screen (**Settings**), and tap **Developer options**. Choose **USB Debugging**.

## Recording & Playing Sounds 

- Check this tutorial from Google: https://developer.android.com/guide/topics/media/mediarecorder#java
- a `MediaPlayer` that you should keep in mind is that it's state-based. That is, the `MediaPlayer` has an internal state that you must always be aware of when writing your code, because certain operations are only valid when then player is in specific states. If you perform an operation while in the wrong state, the system may throw an exception or cause other undesirable behaviors.

## Good Ressource for the MFCC computation 

- https://github.com/chiachunfu/speech
- Hack to add mfcc into the TF custom layers : https://stackoverflow.com/questions/43332342/is-it-possible-to-replace-placeholder-with-a-constant-in-an-existing-graph/43342922#43342922
- Good google TF lite tutorial : https://codelabs.developers.google.com/codelabs/recognize-flowers-with-tensorflow-on-android/#9
- Previous tool to use TF to reshape things in the right way before doing the inference: **TensorFlowInferenceInterface**. The source code is here: https://github.com/tensorflow/tensorflow/blob/master/tensorflow/tools/android/inference_interface/java/org/tensorflow/contrib/android/TensorFlowInferenceInterface.java