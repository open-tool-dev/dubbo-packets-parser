package org.apache.dubbo.parser;

import org.apache.dubbo.parser.parser.TestcaseV6ListParser;
import org.junit.Test;

public class TestcaseV6ListParserTest {

    @Test
    public void test() throws Exception {
        long fileName = System.currentTimeMillis();
        HessianTestcase.doMain(TestcaseV6ListParser.class.getName(), new String[]{
                "--count", "16", "--size", "40960", "--outfile", String.format("/tmp/%s", fileName)
        });
        System.out.println("generate file: " + fileName);
    }
}
