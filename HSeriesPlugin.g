from ..Script import Script


class extension(Script):
    """Allows users to convert g-code to be compatible with Diabase machines.
    """

    def getSettingDataString(self):  # All the extension information is here
        return """{
            "name": "Diabase Post Processor",
            "key": "DiabasePostProcessor",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "main_gcode":
                {
                    "label": "Re-write G-code",
                    "description": "When enabled, the G-code will be modified to be suitable for Diabase machines.",
                    "type": "bool",
                    "default_value": true
                },
                "preheat":
                {
                    "label": "Pre-heat Tools Early",
                    "description": "EXPERIMENTAL - When enabled, this will(in theory) start to preheat tools before they are to be used to improve efficiency.",
                    "type": "bool",
                    "default_value": false
                }
            }
        }"""

    def get_number_from_string(self, string,
                               char_before):  # This is for when we are looking for a number that will always follow a particular character
        number_found, number, int_length = False, '', 0
        for char in string:
            if not number_found:  # This if statement looks for the Identifying char because we know the number will be right after
                if char == char_before:
                    number_found = True
            else:
                if not char.iddigit():
                    break
                else:  # This else block adds each number after the p to a string, and counts how many digits this is so that I can reconstruct the string where the number leaves off.
                    number += char
                    int_length += 1
        return [number, int_length]

    def execute(self, data):  # This is what will actually run when the extension is called
        new_data, new_layer = [], ''
        if self.getSettingValueByKey("main_gcode"):  # Looks for the gcode
            for layer_number, layer in enumerate(data):  # Loop to iterate through all layers
                lines_in_layer = list(data[layer_number].split("\n"))
                for line in lines_in_layer:  # Loop to move through every line in each layer

                    if "M82" in line:  # This deletes all lines containing M82
                        line = ''

                    elif "M109" in line:  # This comments out all lines with M109 commands
                        line = "".join([';', line])

                    elif "G10 P" in line:  # Change G10 P# to G10 P(#+1)

                        g10_number_values = self.get_number_from_string(line, "P")
                        g10_number_string = g10_number_values[0]
                        g10_number_length = g10_number_values[1]
                        new_number_string = str(int(g10_number_string) + 1)
                        string_after_number = line[5 + g10_number_length:len(line)]
                        if " ".join([" Set tool", g10_number_string]) in string_after_number:
                            string_after_number = string_after_number.replace(
                                " ".join([" Set tool", g10_number_string]),
                                " ".join([" Set tool", str(int(
                                    g10_number_string) + 1)]))  # This makes sure the increment is made in the comments as well

                        line = "".join([line[0:5], new_number_string,
                                        string_after_number])  # Replacing the line with the new version where one is added to the number after P

                    elif "M104 T" in line:  # Replace M104 T# S$$$ with G10 P(#+1) S$$$ R($$$-50)
                        m104_t_number_values = self.get_number_from_string(line, "T")
                        m104_s_number_values = self.get_number_from_string(line, "S")

                        line = "".join(["G10 P", str(int(m104_t_number_values[0]) + 1), " S", m104_s_number_values[
                            0], " R", str(int(m104_s_number_values[0]) - 50),
                                        '\n'])

                    elif 'T' in line:  # All remaining lines with T# will be removed completely.
                        for i in range(0, len(line) - 1):
                            if line[i] == 'T' and line[i + 1].isdigit():
                                line = ''
                                break

                    if line != "" and line != "\n" and line != " ":  # Adds the line to the layer if it is not blank
                        new_layer += line
                        new_layer += "\n"

            new_data.append(new_layer)

        if self.getSettingValueByKey("preheat"):
            pass

        return new_data
