package cn.cddes.robot;

import java.io.ByteArrayOutputStream;
import java.util.Arrays;

public class PacketAssembler {

    private static final byte FRAME_HEAD = (byte) 0xAA;

    private ByteArrayOutputStream buffer = new ByteArrayOutputStream();
    private Integer expectedLen = null;
    private Integer lastSeq = null;

    public void reset() {
        buffer.reset();
        expectedLen = null;
        lastSeq = null;
    }

    public byte[] feed(byte[] data) {

        if (data == null || data.length < 4) {
            return null;
        }

        byte head = data[0];
        int seq = data[1] & 0xFF;

        int total = ((data[3] & 0xFF) << 8) | (data[2] & 0xFF); // little endian

        byte[] payload = Arrays.copyOfRange(data, 4, data.length);

        if (head != FRAME_HEAD) {
            System.out.println("❌ bad frame head");
            reset();
            return null;
        }

        if (lastSeq != null && ((lastSeq + 1) & 0xFF) != seq) {
            System.out.println("❌ seq error");
            reset();
            return null;
        }

        if (expectedLen == null) {
            expectedLen = total;
        }

        buffer.write(payload, 0, payload.length);
        lastSeq = seq;

        if (buffer.size() >= expectedLen) {

            byte[] full = buffer.toByteArray();
            byte[] result = Arrays.copyOfRange(full, 0, expectedLen);

            reset();
            return result;
        }

        return null;
    }
}
