package org.apache.dubbo.parser.parser;

import com.beust.jcommander.Parameter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Maps;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.apache.dubbo.common.serialize.hessian2.Hessian2ObjectOutput;
import org.apache.dubbo.parser.testcase.TestcaseMapV1;
import org.apache.dubbo.parser.testcase.TestcaseV8;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.nio.charset.Charset;
import java.util.Map;
import java.util.Random;

public class TestcaseV10MapParser extends AbstractParser {

    @Parameter(names = {"--count"}, required = true)
    private int count;

    @Parameter(names = {"--size"}, required = true)
    private int size;

    @Parameter(names = {"--outfile"}, required = true)
    private String outfile;

    private final Random random;

    public TestcaseV10MapParser(String[] args) {
        super(args);
        this.random = new Random();
    }

    TestcaseV8 generate() {
        StringBuilder builder = new StringBuilder();
        int realSize = random.nextInt(this.size) + 1;
        for (int k = 0; k < realSize; ++k) {
            random.nextInt();
            builder.append((char) (0x4e00 + random.nextInt(0x9fa5 - 0x4e00)));
        }
        TestcaseV8 testcase = new TestcaseV8();
        testcase.setField0(builder.toString());
        testcase.setField1(random.nextInt());
        testcase.setField2((short) random.nextInt());
        testcase.setField3(random.nextLong());
        testcase.setField4(random.nextDouble());
        testcase.setField5(random.nextFloat());
        byte[] bs = new byte[1];
        random.nextBytes(bs);
        testcase.setField6(bs[0]);
        testcase.setField7((char) (0x4e00 + random.nextInt(0x9fa5 - 0x4e00)));
        return testcase;
    }

    @Override
    public void test() throws Exception {
        TestcaseMapV1 testcaseMapV1 = new TestcaseMapV1();
        Map<Character, TestcaseV8> mapChar = Maps.newHashMap();
        for (int t = 0; t < this.count; ++t) {
            TestcaseV8 testcase = generate();
            mapChar.put((char) (0x4e00 + random.nextInt(0x9fa5 - 0x4e00)), testcase);
        }
        testcaseMapV1.setField0(mapChar);
        Map<Byte, TestcaseV8> mapByte = Maps.newHashMap();
        for (int t = 0; t < this.count; ++t) {
            TestcaseV8 testcase = generate();
            byte[] bs = new byte[1];
            random.nextBytes(bs);
            mapByte.put(bs[0], testcase);
        }
        testcaseMapV1.setField1(mapByte);
        Map<Short, TestcaseV8> mapShort = Maps.newHashMap();
        for (int t = 0; t < this.count; ++t) {
            TestcaseV8 testcase = generate();
            mapShort.put((short) random.nextInt(), testcase);
        }
        testcaseMapV1.setField2(mapShort);
        Map<Integer, TestcaseV8> mapI32 = Maps.newHashMap();
        for (int t = 0; t < this.count; ++t) {
            TestcaseV8 testcase = generate();
            mapI32.put(random.nextInt(), testcase);
        }
        testcaseMapV1.setField3(mapI32);
        Map<Long, TestcaseV8> mapI64 = Maps.newHashMap();
        for (int t = 0; t < this.count; ++t) {
            TestcaseV8 testcase = generate();
            mapI64.put(random.nextLong(), testcase);
        }
        testcaseMapV1.setField4(mapI64);
        Map<String, TestcaseV8> mapStr = Maps.newHashMap();
        for (int t = 0; t < this.count; ++t) {
            StringBuilder builder = new StringBuilder();
            int realSize = random.nextInt(this.size) + 1;
            for (int k = 0; k < realSize; ++k) {
                random.nextInt();
                builder.append((char) (0x4e00 + random.nextInt(0x9fa5 - 0x4e00)));
            }
            TestcaseV8 testcase = generate();
            mapStr.put(builder.toString(), testcase);
        }
        testcaseMapV1.setField7(mapStr);
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        Hessian2ObjectOutput hessian2ObjectOutput = new Hessian2ObjectOutput(outputStream);
        hessian2ObjectOutput.writeObject(testcaseMapV1);
        hessian2ObjectOutput.flushBuffer();
        byte[] buf = outputStream.toByteArray();
        final String str = Base64.encodeBase64String(buf);
        String file = String.format("%s.txt", this.outfile);
        FileUtils.write(new File(file), str, Charset.defaultCharset());
        file = String.format("%s.json", this.outfile);
        ObjectMapper mapper = new ObjectMapper();
        FileUtils.write(new File(file), mapper.writeValueAsString(testcaseMapV1), Charset.defaultCharset());
    }
}
