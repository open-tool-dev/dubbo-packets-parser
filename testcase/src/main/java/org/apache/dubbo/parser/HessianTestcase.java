package org.apache.dubbo.parser;

import org.apache.dubbo.parser.parser.AbstractParser;

import java.lang.reflect.Constructor;

public class HessianTestcase {

    public static void main(String[] args) throws Exception {
        String clz = args[0];
        String[] target = new String[]{};
        if (args.length - 1 > 0) {
            target = new String[args.length - 1];
        }
        System.arraycopy(args, 1, target, 0, target.length);
        doMain(clz, target);
    }

    public static void doMain(String clz, String[] args) throws Exception {
        Constructor<?> constructor = Class.forName(clz).getDeclaredConstructor(String[].class);
        AbstractParser parser = (AbstractParser) constructor.newInstance((Object) args);
        parser.parse();
        parser.test();
    }

}
