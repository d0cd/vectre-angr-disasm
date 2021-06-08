from string import Template

platform_def_template = Template(""
                                 "platform $PLATFORM_NAME {\n"
                                 "$BODY"
                                 "\n}")