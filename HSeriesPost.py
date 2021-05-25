from ..Script import Script


class HSeriesPost(Script):
    """Allows users to convert g-code to be compatible with Diabase machines.
    """

    def getSettingDataString(self):
        return """{
            "name": "Diabase Post Processor",
            "key": "DiabasePostProcessor",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "opening_lines":
                {
                    "label": "Modify G-code for H-series",
                    "description": "When enabled, the G-code will be modified to be suitable for Diabase H-series machines.",
                    "type": "bool",
                    "default_value": true
                },
                "preheat":
                {
                    "label": "Pre-heat Tools",
                    "description": "EXPERIMENTAL - When enabled, this will(in theory) start to preheat tools before they are to be used to improve efficiency.",
                    "type": "bool",
                    "default_value": false
                }
            }
        }"""

    def get_number_from_string(self, string, char_before):
        number_found, number, int_length = False, '', 0
        for char in string:
            if not number_found:  # This if statement looks for the first P because we know the number will be right after
                if char == char_before:
                    number_found = True
            else:
                if char == ' ' or char == "\n":  # This looks for a space because once a space is found, the number has ended. This is useful in case the number is ever multiple digits.
                    break
                else:  # This else block adds each number after the p to a string, and counts how many digits this is so that I can reconstruct the string where the number leaves off.
                    number += char
                    int_length += 1
        return [number, int_length]

    def execute(self, data):
        new_data, new_layer, looking_for_retraction, looking_for_extrusion, found_extrusion, looking_for_swap, found_swap, first_tool, swap_value = [], [], False, False, False, False, False, True, ""
        if self.getSettingValueByKey("opening_lines"):
            for layer_number, layer in enumerate(
                    data):  # Big loop to iterate through all layers
                lines_in_layer = list(data[layer_number].split("\n"))
                for line in lines_in_layer:  # Loop to move through every line in each layer

                    if ";Extruder " in line and line[
                        len(line) - 1].isdigit():  # Looks for comments in the G-code that mention the changing of the extruder.
                        # When the extruder changes, there are lots of things we have to look for.
                        looking_for_retraction = True
                        looking_for_extrusion = True
                        looking_for_swap = True

                        if self.getSettingValueByKey("preheat"):  # This places a preheat line 10 lines before the tool is used
                            if not first_tool:  # It checks to make sure it is not the first tool.
                                # If we try to preheat the first tool, it will try to place the preheat line before the file even starts.
                                if len(new_layer) >= 10:  # This next section checks if there are at least 10 lines to place the pre-heat line back
                                    new_layer.insert(len(new_layer) - 11, "".join(
                                        ["M563 P", str(int(line[len(line) - 1]) + 1), " A2 ; Pre-heating tool"]))
                                else:  # If there are not 10 lines to place the preheat line back, it gets placed as far back as possible.
                                    new_layer.insert(0, "".join(
                                        ["M563 P", str(int(line[len(line) - 1]) + 1), " A2 ; Pre-heating tool"]))
                            first_tool = False

                    if ";TYPE" in line and looking_for_extrusion:  # Once ";TYPE" is found, this sets a flag variable to true, indicating that we are looking to turn a G1 into a G11
                        looking_for_extrusion = False
                        found_extrusion = True

                    if "M82" in line:
                        line = ''  # This simply deletes all lines containing M82

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
                            0], " R", str(int(m104_s_number_values[0]) - 50)])

                    elif 'T' in line:  # All remaining lines with T# will be removed completely.
                        for i in range(0, len(line) - 1):
                            if line[i] == 'T' and line[i + 1].isdigit():
                                line = ''
                                break

                    elif ";Extruder end code" in line:  # Replace final retraction with “G10” (2 lines above ;Extruder end code)
                        if len(new_layer) >= 3:
                            new_layer[len(new_layer) - 2] = 'G10; Edited from G1 to G10'
                        else:
                            new_layer.append(";LAYER PROCESSING ERROR(editing G1 to G10)")  # Error catching, hopefully will never print

                    elif "G1 " in line and looking_for_retraction:  # Remove post-tool-change Retraction
                        line = "".join(['; Retraction Line Removed(', line, ')'])
                        looking_for_retraction = False

                    elif "G1 " in line and found_extrusion:  # Replace post-tool-change Extrusions with “G11”
                        line = 'G11; Edited from G1 to G11'
                        found_extrusion = False

                    elif (looking_for_swap or found_swap) and " X" in line and " Y" in line and " Z" in line:  # Catches case where no swap is needed
                        swap_value = ''
                        looking_for_swap = False
                        found_swap = False

                    elif looking_for_swap and "G1" in line and " Z" in line:  # Stores the first swap value
                        swap_value = line
                        looking_for_swap = False
                        found_swap = True

                    elif found_swap and " X" in line and " Y" in line:  # Complete the swap(wap XY move with Z move after tool-change)
                        if len(new_layer) >= 3:
                            new_layer[len(new_layer) - 2] = " ".join(
                                [line, ";Swapped"])
                            line = " ".join(
                                [swap_value, ";Swapped"])
                        else:
                            new_layer.append(";LAYER PROCESSING ERROR(Swapping)")  # Error catching, hopefully will never print
                        swap_value = ''
                        found_swap = False

                    if line != "" and line != "\n" and line != " ":  # Adds the edited line back to the layer if it is not blank
                        new_layer.append(line)

            new_data.append('\n'.join([str(elem) for elem in new_layer]))  # Adds the layer to the data

        return new_data
