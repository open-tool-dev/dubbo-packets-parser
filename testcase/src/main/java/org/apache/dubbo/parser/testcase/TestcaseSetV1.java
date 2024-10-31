package org.apache.dubbo.parser.testcase;

import lombok.Getter;
import lombok.Setter;

import java.io.Serializable;
import java.util.Date;
import java.util.Set;

@Getter
@Setter
public class TestcaseSetV1 implements Serializable {

    private Set<Character> field0;

    private Set<Byte> field1;

    private Set<Short> field2;

    private Set<Integer> field3;

    private Set<Long> field4;

    private Set<Float> field5;

    private Set<Double> field6;

    private Set<String> field7;

    private Set<Date> field8;

    private Set<TestcaseV8> field9;

}
