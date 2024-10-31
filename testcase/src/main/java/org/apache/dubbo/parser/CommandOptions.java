package org.apache.dubbo.parser;

import com.beust.jcommander.Parameter;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CommandOptions {

    @Parameter(names = {"--pcap.result.file"}, required = true)
    private String pcapFile;

    @Parameter(names = {"--elastic.addr"}, required = true)
    private String elasticAddr;

    @Parameter(names = {"--elastic.user"})
    private String userName;

    @Parameter(names = {"--elastic.password"})
    private String password;

}
