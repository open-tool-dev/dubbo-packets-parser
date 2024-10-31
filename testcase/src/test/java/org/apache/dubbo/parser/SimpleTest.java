package org.apache.dubbo.parser;

import com.google.common.collect.Lists;
import lombok.Getter;
import lombok.Setter;
import org.apache.commons.codec.binary.Base64;
import org.apache.dubbo.common.serialize.hessian2.Hessian2ObjectOutput;
import org.junit.Test;

import java.io.ByteArrayOutputStream;
import java.io.Serializable;
import java.util.List;

public class SimpleTest {

    @Test
    public void test() throws Exception {
        ByteArrayOutputStream bout = new ByteArrayOutputStream();
        Hessian2ObjectOutput out = new Hessian2ObjectOutput(bout);
        List<Debug> list = Lists.newArrayList();
        Debug debug = new Debug();
        debug.setName("name");
        list.add(debug);
        list.add(debug);
        out.writeObject(list);
        out.flushBuffer();
        System.out.println(new String(Base64.encodeBase64(bout.toByteArray())));
    }

    @Getter
    @Setter
    public static class Debug implements Serializable {

        private String name;

    }
}
