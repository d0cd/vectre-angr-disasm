from string import Template

adversary_template = Template("module adversary {\n"
                              "\n"
                              "    input spec_enabled : boolean;\n"
                              "    instance prog : program(spec_enabled : (spec_enabled));\n\n"
                              ""
                              "    // Define any additional procedures for the adversary.\n\n"
                              ""
                              "    init {\n"
                              "        // Define any initial state for the adversary"
                              "    }\n\n"
                              ""
                              "    next {\n"
                              "        // Define the execution of the adversary and the program."
                              "        // Default is just running the program."
                              "        next(prog);"
                              "    }\n"
                              "}")