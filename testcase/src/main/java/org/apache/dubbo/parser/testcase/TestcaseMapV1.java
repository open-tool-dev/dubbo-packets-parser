package org.apache.dubbo.parser.testcase;

import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;
import java.util.Date;
import java.util.Map;

@Getter
@Setter
public class TestcaseMapV1 implements Serializable  {

    private Map<Character, TestcaseV8> field0;

    private Map<Byte, TestcaseV8> field1;

    private Map<Short, TestcaseV8> field2;

    private Map<Integer, TestcaseV8> field3;

    private Map<Long, TestcaseV8> field4;

    private Map<String, TestcaseV8> field7;

}
