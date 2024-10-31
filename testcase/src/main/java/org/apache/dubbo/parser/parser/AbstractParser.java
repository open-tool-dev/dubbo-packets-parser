package org.apache.dubbo.parser.parser;

import com.beust.jcommander.JCommander;

public abstract class AbstractParser {

    private String[] args;

    public AbstractParser(String[] args) {
        this.args = args;
    }

    public void parse() {
        JCommander commander = JCommander.newBuilder().addObject(this).build();
        commander.parse(this.args);
    }

    public abstract void test() throws Exception;

}
