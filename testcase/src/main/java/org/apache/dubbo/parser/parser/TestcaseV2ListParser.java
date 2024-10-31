package org.apache.dubbo.parser.parser;

import com.beust.jcommander.Parameter;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.common.collect.Lists;
import org.apache.commons.codec.binary.Base64;
import org.apache.commons.io.FileUtils;
import org.apache.dubbo.common.serialize.hessian2.Hessian2ObjectOutput;
import org.apache.dubbo.parser.testcase.TestcaseV2;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.nio.charset.Charset;
import java.util.List;
import java.util.Random;

public class TestcaseV2ListParser extends AbstractParser {

    @Parameter(names = {"--count"}, required = true)
    private int count;

    @Parameter(names = {"--size"}, required = true)
    private int size;

    @Parameter(names = {"--outfile"}, required = true)
    private String outfile;

    private final Random random;

    public TestcaseV2ListParser(String[] args) {
        super(args);
        this.random = new Random();
    }

    @Override
    public void test() throws Exception {
        final List<TestcaseV2> list = Lists.newArrayListWithCapacity(this.count);
        for (int t = 0; t < this.count; ++t) {
            StringBuilder builder = new StringBuilder();
            int realSize = random.nextInt(this.size) + 1;
            for (int k = 0; k < realSize; ++k) {
                random.nextInt();
                builder.append((char) (0x4e00 + random.nextInt(0x9fa5 - 0x4e00)));
            }
            TestcaseV2 testcase = new TestcaseV2();
            testcase.setField0(builder.toString());
            testcase.setField1(random.nextInt());
            list.add(testcase);
        }
        ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
        Hessian2ObjectOutput hessian2ObjectOutput = new Hessian2ObjectOutput(outputStream);
        hessian2ObjectOutput.writeObject(list);
        hessian2ObjectOutput.flushBuffer();
        byte[] buf = outputStream.toByteArray();
        final String str = Base64.encodeBase64String(buf);
        String file = String.format("%s.txt", this.outfile);
        FileUtils.write(new File(file), str, Charset.defaultCharset());
        file = String.format("%s.json", this.outfile);
        ObjectMapper mapper = new ObjectMapper();
        FileUtils.write(new File(file), mapper.writeValueAsString(list), Charset.defaultCharset());
    }
}
