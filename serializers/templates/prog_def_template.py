from string import Template

prog_def_template = Template("prog ${PROG_NAME} {\n"
                            "${BASIC_BLOCKS}\n"
                            "}\n")