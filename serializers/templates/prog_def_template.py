from string import Template

prog_def_template = Template("prog ${PROGNAME} {\n"
                            "    ${BASIC_BLOCKS}\n"
                            "}")