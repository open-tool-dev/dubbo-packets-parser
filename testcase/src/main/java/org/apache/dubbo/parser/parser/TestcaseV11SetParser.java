package org.apache.dubbo.parser.parser;

import com.beust.jcommander.Parameter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Sets;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.apache.dubbo.common.serialize.hessian2.Hessian2ObjectOutput;
import org.apache.dubbo.parser.testcase.TestcaseSetV1;
import org.apache.dubbo.parser.testcase.TestcaseV8;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.nio.charset.Charset;
import java.util.Random;
import java.util.Set;

public class TestcaseV11SetParser extends AbstractParser {

    @Parameter(names = {"--count"}, required = true)
    private int count;

    @Parameter(names = {"--size"}, required = true)
    private int size;

    @Parameter(names = {"--outfile"}, required = true)
    private String outfile;

    private final Random random;

    public TestcaseV11SetParser(String[] args) {
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
        TestcaseSetV1 testcaseMapV1 = new TestcaseSetV1();
        Set<Character> setChar = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            setChar.add((char) (0x4e00 + random.nextInt(0x9fa5 - 0x4e00)));
        }
        testcaseMapV1.setField0(setChar);
        Set<Byte> setByte = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            byte[] bs = new byte[1];
            random.nextBytes(bs);
            setByte.add(bs[0]);
        }
        testcaseMapV1.setField1(setByte);
        Set<Short> setShort = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            setShort.add((short) random.nextInt());
        }
        testcaseMapV1.setField2(setShort);
        Set<Integer> setI32 = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            setI32.add(random.nextInt());
        }
        testcaseMapV1.setField3(setI32);
        Set<Long> setI64 = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            setI64.add(random.nextLong());
        }
        testcaseMapV1.setField4(setI64);
        Set<Float> setFloat = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            setFloat.add(random.nextFloat());
        }
        testcaseMapV1.setField5(setFloat);
        Set<Double> setDouble = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            setDouble.add(random.nextDouble());
        }
        testcaseMapV1.setField6(setDouble);
        Set<String> setStr = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            StringBuilder builder = new StringBuilder();
            int realSize = random.nextInt(this.size) + 1;
            for (int k = 0; k < realSize; ++k) {
                random.nextInt();
                builder.append((char) (0x4e00 + random.nextInt(0x9fa5 - 0x4e00)));
            }
            setStr.add(builder.toString());
        }
        testcaseMapV1.setField7(setStr);
        Set<TestcaseV8> set = Sets.newHashSet();
        for (int t = 0; t < this.count; ++t) {
            set.add(generate());
        }
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
