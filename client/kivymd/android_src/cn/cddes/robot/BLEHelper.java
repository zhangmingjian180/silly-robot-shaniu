package cn.cddes.robot;

import android.bluetooth.*;
import android.bluetooth.le.*;
import android.app.Activity;
import android.content.Context;

import android.util.Log;

import java.util.*;
import java.util.concurrent.CountDownLatch;

public class BLEHelper {
    private final BluetoothAdapter adapter;
    private final Context ctx;
    private final Activity activity;
    private final ScanCallback scanCallback;
    private final BluetoothGattCallback gattCallback;
    private HashSet<String> set;
    private BluetoothGatt gatt;
    private boolean isConnectSuccess;
    private byte[] readResult;
    private boolean writeResult;
    private byte[] notifyResult;
    private int wifiStatus;
    private CountDownLatch connectDone;
    private CountDownLatch readDone;
    private CountDownLatch writeDone;
    private CountDownLatch notifyDone;
    private PacketAssembler assembler;

    private static enum NOTIFY_TYPE {NORMAL, WIFI};
    private NOTIFY_TYPE currentNotifyType;

    public interface NotifyListener {
        void onNotify(byte[] data);
    }

    private NotifyListener notifyListener;

    public BLEHelper(Activity activity) {
        this.activity = activity;
        ctx = activity.getApplicationContext();
        BluetoothManager m =
            (BluetoothManager) ctx.getSystemService(Context.BLUETOOTH_SERVICE);
        adapter = m.getAdapter();
        set = null;
        currentNotifyType = NOTIFY_TYPE.NORMAL;
        scanCallback = new ScanCallback() {
            @Override
            public void onScanResult(int callbackType, ScanResult result) {
                String name = null;
                ScanRecord record = result.getScanRecord();
                if (record != null) {
                    name = record.getDeviceName();
                }
                if (Objects.equals(name, "RobotBLE"))
                    BLEHelper.this.set.add(result.getDevice().getAddress());
            }

            @Override
            public void onScanFailed(int errorCode) {
                Log.e("BLE", "failed to scan: " + errorCode);
            }
        };
        gattCallback = new BluetoothGattCallback() {
            @Override
            public void onConnectionStateChange(
                    BluetoothGatt gatt,
                    int status,
                    int newState) {
                if (status == BluetoothGatt.GATT_SUCCESS &&
                        newState == BluetoothProfile.STATE_CONNECTED) {
                    Log.i("BLE", "Connected");
                    gatt.discoverServices();
                } else {
                    Log.e("BLE", "Disconnected status=" + status);
                    gatt.close();
                    connectDone.countDown();
                }
            }

            @Override
            public void onServicesDiscovered(
                    BluetoothGatt gatt,
                    int status) {
                if (status != BluetoothGatt.GATT_SUCCESS) isConnectSuccess = false;
                else isConnectSuccess = true;
                connectDone.countDown();
            }

            @Override
            public void onCharacteristicRead(
                    BluetoothGatt gatt,
                    BluetoothGattCharacteristic ch,
                    int status) {
                if (status != BluetoothGatt.GATT_SUCCESS) {
                    Log.e("BLE", "Read failed status=" + status);
                    readDone.countDown();
                    return;
                }
                Log.i("BLE", "Read Success");
                readResult = ch.getValue();
                Log.i("BLE", "readResult len=" + readResult.length);
                readDone.countDown();
            }

            @Override
            public void onCharacteristicWrite(
                    BluetoothGatt gatt,
                    BluetoothGattCharacteristic ch,
                    int status) {
                if (status != BluetoothGatt.GATT_SUCCESS) {
                    Log.e("BLE", "Write failed status=" + status);
                    writeResult = false;
                    writeDone.countDown();
                    return;
                }
                Log.i("BLE", "Write Success");
                writeResult = true;
                writeDone.countDown();
            }

            @Override
            public void onCharacteristicChanged(BluetoothGatt gatt,
                    BluetoothGattCharacteristic characteristic) {
                byte[] data = characteristic.getValue();
                Log.i("BLE", "original receive notify data: " + data.length);
                switch (currentNotifyType) {
                    case NORMAL: {
                        notifyResult = assembler.feed(data);
                        if (notifyResult != null) {
                            Log.i("BLE", "✅ complete message: " + notifyResult.length);
                            notifyDone.countDown();
                        }
                    }; break;
                    case WIFI: {
                        if (data.length < 1) {
                            wifiStatus = 1;
                            notifyDone.countDown();
                            return;
                        }
                        int num;
                        if (data.length == 1) num = (int) (data[0] & 0xFF);
                        else num = 1;
                        Log.i("BLE", "status: " + num);
                        if (num != 255) {
                            wifiStatus = num;
                            notifyDone.countDown();
                        }
                    }; break;
                }
            }
        };
    }

    public String[] getResultsAddress() {
        return set.toArray(new String[0]);
    }

    /* ========= scan ========= */
    public void startScan() {
        Log.i("BLE", "start scanning");
        ScanSettings scanSettings = new ScanSettings.Builder()
            .setScanMode(ScanSettings.SCAN_MODE_LOW_LATENCY)
            .setCallbackType(ScanSettings.CALLBACK_TYPE_ALL_MATCHES)
            .setMatchMode(ScanSettings.MATCH_MODE_AGGRESSIVE)
            .setNumOfMatches(ScanSettings.MATCH_NUM_ONE_ADVERTISEMENT)
            .build();
        set = new  HashSet<String>();
        adapter.getBluetoothLeScanner().startScan(null, scanSettings, scanCallback);
    }

    public void stopScan() {
        Log.i("BLE", "finish scanning");
        adapter.getBluetoothLeScanner().stopScan(scanCallback);
        Log.i("BLE", "finished scan");
    }

    /* ========= connect ========= */
    public boolean connect(String addr) {
        isConnectSuccess = false;
        connectDone = new CountDownLatch(1);
        gatt = adapter.getRemoteDevice(addr).connectGatt(ctx, false, gattCallback);
        try {
            connectDone.await();
        }
        catch (InterruptedException e) {
            e.printStackTrace();
        }
        return isConnectSuccess;
    }

    /* ========= read ========= */
    private boolean startRead(UUID svc, UUID ch) {
        Log.i("BLE", "try to send read require");
        BluetoothGattService service = gatt.getService(svc);
        if (service == null) {
            Log.e("BLE", "service null");
            return false;
        }
        BluetoothGattCharacteristic c = service.getCharacteristic(ch);
        if (c == null) {
            Log.e("BLE", "char null");
            return false;
        }
        boolean status = gatt.readCharacteristic(c);
        if (!status) {
            Log.e("BLE", "failed to send read require");
            return false;
        }
        Log.i("BLE", "success to send read require");
        return true;
    }

    public byte[] read(UUID svc, UUID ch) {
        Log.i("BLE", "try to read");
        readResult = new byte[0];
        readDone = new CountDownLatch(1);
        if (!startRead(svc, ch)) {
            readDone = null;
            return new byte[0];
        }
        try {
            readDone.await();
        }
        catch (InterruptedException e) {
            e.printStackTrace();
        }
        return readResult;
    }

    /* ========= write ========= */
    private boolean startWrite(UUID svc, UUID ch, byte[] data) {
        Log.i("BLE", "try to send write require");
        BluetoothGattService service = gatt.getService(svc);
        if (service == null) {
            Log.e("BLE", "service null");
            return false;
        }
        BluetoothGattCharacteristic c = service.getCharacteristic(ch);
        if (c == null) {
            Log.e("BLE", "char null");
            return false;
        }
        boolean status = c.setValue(data);
        if (!status) {
            Log.e("BLE", "failed to setValue");
            return false;
        }
        status = gatt.writeCharacteristic(c);
        if (!status) {
            Log.e("BLE", "failed to send write require");
            return false;
        }
        Log.i("BLE", "success to send write require");
        return true;
    }

    public boolean write(UUID svc, UUID ch, byte[] data) {
        Log.i("BLE", "try to write");
        writeResult = false;
        writeDone = new CountDownLatch(1);
        if (!startWrite(svc, ch, data)) {
            writeDone = null;
            return false;
        }
        try {
            writeDone.await();
        }
        catch (InterruptedException e) {
            e.printStackTrace();
        }
        return writeResult;
    }

    private boolean startNotify(UUID svc, UUID ch) {
        Log.i("BLE", "try to send notify require");
        BluetoothGattService service = gatt.getService(svc);
        if (service == null) {
            Log.e("BLE", "service null");
            return false;
        }
        BluetoothGattCharacteristic c = service.getCharacteristic(ch);
        if (c == null) {
            Log.e("BLE", "char null");
            return false;
        }
        boolean status = gatt.setCharacteristicNotification(c, true);
        if (!status) {
            Log.e("BLE", "failed to setCharacteristicNotification");
            return false;
        }
        BluetoothGattDescriptor d =
            c.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"));
        status = d.setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE);
        if (!status) {
            Log.e("BLE", "failed to setValue(BluetoothGattDescriptor.ENABLE_NOTIFICATION_VALUE)");
            return false;
        }
        status = gatt.writeDescriptor(d);
        if (!status) {
            Log.e("BLE", "failed to writeDescriptor");
            return false;
        }
        Log.i("BLE", "success to start notify");
        return true;
    }

    private boolean stopNotify(UUID svc, UUID ch) {
        BluetoothGattService service = gatt.getService(svc);
        if (service == null) return false;
        BluetoothGattCharacteristic c = service.getCharacteristic(ch);
        if (c == null) return false;
        gatt.setCharacteristicNotification(c, false);
        BluetoothGattDescriptor d =
            c.getDescriptor(UUID.fromString("00002902-0000-1000-8000-00805f9b34fb"));
        d.setValue(BluetoothGattDescriptor.DISABLE_NOTIFICATION_VALUE);
        return gatt.writeDescriptor(d);
    }

    public byte[] notify(UUID svc, UUID ch) {
        Log.i("BLE", "try to notify");
        assembler = new PacketAssembler();
        notifyResult = new byte[0];
        notifyDone = new CountDownLatch(1);
        currentNotifyType = NOTIFY_TYPE.NORMAL;
        if (!startNotify(svc, ch)) {
            Log.i("BLE", "failed to start notify java");
            notifyDone = null;
            return new byte[0];
        }
        try {
            Log.i("BLE", "waite for notifyDone");
            notifyDone.await();
        }
        catch (InterruptedException e) {
            e.printStackTrace();
        }
        if (!stopNotify(svc, ch)) {
            Log.i("BLE", "failed to stop notify java");
            notifyDone = null;
            return new byte[0];
        }
        Log.i("BLE", "success to notify java");
        return notifyResult;
    }

    public int getWifiStatus(UUID svc, UUID ch) {
        Log.i("BLE", "try to getWifiStatus");
        wifiStatus = 1;
        notifyDone = new CountDownLatch(1);
        currentNotifyType = NOTIFY_TYPE.WIFI;
        if (!startNotify(svc, ch)) {
            notifyDone = null;
            return 1;
        }
        try {
            notifyDone.await();
        }
        catch (InterruptedException e) {
            e.printStackTrace();
        }
        if (!stopNotify(svc, ch)) {
            notifyDone = null;
            return 1;
        }
        return wifiStatus;
    }
}
