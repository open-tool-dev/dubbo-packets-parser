package org.apache.dubbo.parser;

import org.apache.dubbo.parser.parser.TestcaseV1ListParser;
import org.junit.Test;

public class TestcaseV1ListParserTest {

    @Test
    public void test() throws Exception {
        long fileName = System.currentTimeMillis();
        HessianTestcase.doMain(TestcaseV1ListParser.class.getName(), new String[]{
                "--count", "16", "--size", "40960", "--outfile", String.format("/tmp/%s", fileName)
        });
        System.out.println("generate file: " + fileName);
    }
}
