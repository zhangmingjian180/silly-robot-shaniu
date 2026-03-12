package cn.cddes.robot;

import java.util.concurrent.CountDownLatch;
import java.util.UUID;

import android.Manifest;
import android.os.Build;
import android.content.pm.PackageManager;
import android.util.Log;
import org.kivy.android.PythonActivity;

public class MainActivity extends PythonActivity {
    private static final int timeoutSeconds = 5;
    private static String[] robotList;
    private static CountDownLatch requestPermissionsDone;
    private static boolean isPermissionsGranted;
    public static final int REQUEST_BLE_PERMISSION = 1001;

    public static String[] getRobotList() {
        if (scanBluetooth()) return robotList;
        else return new String[0];
    }

    public static byte[] getInfo(String service, String characteristic, String addr) {
        BLEHelper ble = new BLEHelper(PythonActivity.mActivity);
        if (!ble.connect(addr)) return new byte[0];
        return ble.read(UUID.fromString(service), UUID.fromString(characteristic));
    }

    public static byte[] getWifiList(String service, String characteristic, String addr) {
        BLEHelper ble = new BLEHelper(PythonActivity.mActivity);
        if (!ble.connect(addr)) return new byte[0];
        return ble.notify(UUID.fromString(service), UUID.fromString(characteristic));
    }

    public static int connectWifi(String service, String characteristicWifiCon,
        String characteristicWifiStatus, String addr, byte[] data) {
        BLEHelper ble = new BLEHelper(PythonActivity.mActivity);
        if (!ble.connect(addr)) return 1;
        if (!ble.write(UUID.fromString(service),
                UUID.fromString(characteristicWifiCon), data)) return 1;
        return ble.getWifiStatus(UUID.fromString(service),
                UUID.fromString(characteristicWifiStatus));
    }

    @Override
    public void onRequestPermissionsResult(
            int requestCode,
            String[] permissions,
            int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == REQUEST_BLE_PERMISSION) {
            if (grantResults.length > 0
                    && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Log.i("BLE", "get permission in onRequestPermissionsResult");
                isPermissionsGranted = true;
            } else {
                Log.i("BLE", "can not get permission in onRequestPermissionsResult");
                isPermissionsGranted = false;
            }
        }
        requestPermissionsDone.countDown();
    }

    public static void scanBluetoothInner() {
        BLEHelper ble = new BLEHelper(PythonActivity.mActivity);
        ble.startScan();

        try {
            Thread.sleep(timeoutSeconds * 1000L);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        ble.stopScan();
        robotList = ble.getResultsAddress();
    }

    public static boolean scanBluetooth() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            if (PythonActivity.mActivity.getApplicationContext().checkSelfPermission(Manifest.permission.BLUETOOTH_SCAN)
                    != PackageManager.PERMISSION_GRANTED) {
                Log.i("BLE", "require permission BLUETOOTH_SCAN");
                PythonActivity.mActivity.requestPermissions(
                    new String[] {Manifest.permission.BLUETOOTH_SCAN},
                    REQUEST_BLE_PERMISSION
                );
                return false;
            }
        } else {
            // Android 6–11
            if (PythonActivity.mActivity.getApplicationContext().checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
                    != PackageManager.PERMISSION_GRANTED ||
                PythonActivity.mActivity.getApplicationContext().checkSelfPermission(Manifest.permission.BLUETOOTH_ADMIN)
                    != PackageManager.PERMISSION_GRANTED) {
                Log.i("BLE", "require permission ACCESS_FINE_LOCATION & BLUETOOTH_ADMIN");
                PythonActivity.mActivity.requestPermissions(
                    new String[] {
                        Manifest.permission.ACCESS_FINE_LOCATION,
                        Manifest.permission.BLUETOOTH_ADMIN
                    },
                    REQUEST_BLE_PERMISSION
                );
                requestPermissionsDone = new CountDownLatch(1);
                isPermissionsGranted = false;
                try {
                    try {
                        requestPermissionsDone.await();
                    }
                    catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                finally {
                    if (!isPermissionsGranted) return false;
                    scanBluetoothInner();
                    return true;
                }
            }
        }
        Log.i("BLE", "granted permission");
        scanBluetoothInner();
        return true;
    }
}
