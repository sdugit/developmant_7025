#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Copyright 2011, The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys

def RemoveAnnotation(line):
    if line.find(":") >= 0:
        annotation = line[line.find(":"): line.find(" ", line.find(":"))]
        return line.replace(annotation, "*")
    else:
        return line

if __name__ == "__main__":
    externs = []
    lines = open("../../../frameworks/base/opengl/libs/GLES2_dbg/gl2_api_annotated.in").readlines()
    output = open("src/com/android/glesv2debugger/MessageParser.java", "w")

    i = 0
    output.write("""\
/*
 ** Copyright 2011, The Android Open Source Project
 **
 ** Licensed under the Apache License, Version 2.0 (the "License");
 ** you may not use this file except in compliance with the License.
 ** You may obtain a copy of the License at
 **
 **     http://www.apache.org/licenses/LICENSE-2.0
 **
 ** Unless required by applicable law or agreed to in writing, software
 ** distributed under the License is distributed on an "AS IS" BASIS,
 ** WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 ** See the License for the specific language governing permissions and
 ** limitations under the License.
 */

// auto generated by generate_MessageParser_java.py,
//  which also prints skeleton code for MessageParserEx.java

package com.android.glesv2debugger;

import com.android.glesv2debugger.DebuggerMessage.Message;
import com.android.glesv2debugger.DebuggerMessage.Message.Function;
import com.google.protobuf.ByteString;

import java.nio.ByteBuffer;

public abstract class MessageParser {

    String args;

    String[] GetList()
    {
        assert args.charAt(0) == '{';
        String arg = args;
        args = args.substring(args.lastIndexOf('}') + 1);
        int comma = args.indexOf(',');
        if (comma >= 0)
            args = args.substring(comma + 1).trim();
        else
            args = null;
        arg = arg.substring(1, arg.lastIndexOf('}')).trim();
        return arg.split(",");
    }

    ByteString ParseFloats(int count) {
        ByteBuffer buffer = ByteBuffer.allocate(count * 4);
        String [] arg = GetList();
        for (int i = 0; i < count; i++)
            buffer.putFloat(Float.parseFloat(arg[i].trim()));
        return ByteString.copyFrom(buffer);
    }

    ByteString ParseInts(int count) {
        ByteBuffer buffer = ByteBuffer.allocate(count * 4);
        String [] arg = GetList();
        for (int i = 0; i < count; i++)
            buffer.putInt(Integer.parseInt(arg[i].trim()));
        return ByteString.copyFrom(buffer);
    }

    ByteString ParseUInts(int count) {
        ByteBuffer buffer = ByteBuffer.allocate(count * 4);
        String [] arg = GetList();
        for (int i = 0; i < count; i++)
            buffer.putInt((int)(Long.parseLong(arg[i].trim()) & 0xffffffff));
        return ByteString.copyFrom(buffer);
    }

    ByteString ParseMatrix(int columns, int count) {
        return ParseFloats(columns * count);
    }

    ByteString ParseString() {
        // TODO: escape sequence and proper string literal
        String arg = args.substring(args.indexOf('"') + 1, args.lastIndexOf('"'));
        args = args.substring(args.lastIndexOf('"'));
        int comma = args.indexOf(',');
        if (comma >= 0)
            args = args.substring(comma + 1).trim();
        else
            args = null;
        return ByteString.copyFromUtf8(arg);
    }

    String GetArgument()
    {
        int comma = args.indexOf(",");
        String arg = null;
        if (comma >= 0)
        {
            arg = args.substring(0, comma).trim();
            args = args.substring(comma + 1).trim();
        }
        else
        {
            arg = args;
            args = null;
        }
        if (arg.indexOf("=") >= 0)
            arg = arg.substring(arg.indexOf("=") + 1);
        return arg;
    }

    int ParseArgument()
    {
        String arg = GetArgument();
        if (arg.startsWith("GL_"))
            return GLEnum.valueOf(arg).value;
        else if (arg.toLowerCase().startsWith("0x"))
            return Integer.parseInt(arg.substring(2), 16);
        else
            return Integer.parseInt(arg);
    }

    int ParseFloat()
    {
        String arg = GetArgument();
        return Float.floatToRawIntBits(Float.parseFloat(arg));
    }

    public void Parse(final Message.Builder builder, String string) {
        int lparen = string.indexOf("("), rparen = string.lastIndexOf(")");
        String s = string.substring(0, lparen).trim();
        args = string.substring(lparen + 1, rparen);
        String[] t = s.split(" ");
        Function function = Function.valueOf(t[t.length - 1]);
        builder.setFunction(function);
        switch (function) {
""")

    abstractParsers = ""

    for line in lines:
        if line.find("API_ENTRY(") >= 0: # a function prototype
            returnType = line[0: line.find(" API_ENTRY(")].replace("const ", "")
            functionName = line[line.find("(") + 1: line.find(")")] #extract GL function name
            parameterList = line[line.find(")(") + 2: line.find(") {")]

            parameters = parameterList.split(',')
            paramIndex = 0

            #if returnType != "void":
            #else:

            if parameterList == "void":
                parameters = []
            inout = ""

            paramNames = []
            abstract = False
            argumentSetters = ""
            output.write("\
            case %s:\n" % (functionName))

            for parameter in parameters:
                parameter = parameter.replace("const","")
                parameter = parameter.strip()
                paramType = parameter.split(' ')[0]
                paramName = parameter.split(' ')[1]
                annotation = ""

                argumentParser = ""

                if parameter.find(":") >= 0:
                    dataSetter = ""
                    assert inout == "" # only one parameter should be annotated
                    inout = paramType.split(":")[2]
                    annotation = paramType.split(":")[1]
                    paramType = paramType.split(":")[0]
                    count = 1
                    countArg = ""
                    if annotation.find("*") >= 0: # [1,n] * param
                        count = int(annotation.split("*")[0])
                        countArg = annotation.split("*")[1]
                        assert countArg in paramNames
                    elif annotation in paramNames:
                        count = 1
                        countArg = annotation
                    elif annotation == "GLstring":
                        annotation = annotation
                    else:
                        count = int(annotation)

                    if paramType == "GLfloat":
                        argumentParser = "ParseFloats"
                    elif paramType == "GLint":
                        argumentParser = "ParseInts"
                    elif paramType == "GLuint":
                        argumentParser = "ParseUInts"
                    elif annotation == "GLstring":
                        assert paramType == 'GLchar'
                    elif paramType.find("void") >= 0:
                        assert 1
                    else:
                        assert 0

                    if functionName.find('Matrix') >= 0:
                        columns = int(functionName[functionName.find("fv") - 1: functionName.find("fv")])
                        assert columns * columns == count
                        assert countArg != ""
                        assert paramType == "GLfloat"
                        dataSetter = "builder.setData(ParseMatrix(%d, %d * builder.getArg%d()));" % (
                            columns, count, paramNames.index(countArg))
                    elif annotation == "GLstring":
                        dataSetter = "builder.setData(ParseString());"
                    elif paramType.find("void") >= 0:
                        dataSetter = "// TODO"
                        abstract = True
                    elif countArg == "":
                        dataSetter = "builder.setData(%s(%d));" % (argumentParser, count)
                    else:
                        dataSetter = "builder.setData(%s(%d * builder.getArg%d()));" % (
                            argumentParser, count, paramNames.index(countArg))
                    argumentSetters += "\
                %s // %s %s\n" % (dataSetter, paramType, paramName)
                else:
                    if paramType == "GLfloat" or paramType == "GLclampf":
                        argumentSetters += "\
                builder.setArg%d(ParseFloat()); // %s %s\n" % (
                    paramIndex, paramType, paramName)
                    elif paramType.find("*") >= 0:
                        argumentSetters += "\
                // TODO: %s %s\n" % (paramType, paramName)
                        abstract = True
                    else:
                        argumentSetters += "\
                builder.setArg%d(ParseArgument()); // %s %s\n" % (
                    paramIndex, paramType, paramName)
                paramNames.append(paramName)
                paramIndex += 1

            if not abstract:
                output.write("%s" % argumentSetters)
            else:
                output.write("\
                Parse_%s(builder);\n" % functionName)
                abstractParsers += "\
    abstract void Parse_%s(Message.Builder builder);\n" % functionName
                print """\
    @Override
    void Parse_%s(Message.Builder builder) {
%s    }
""" % (functionName, argumentSetters) # print skeleton code for MessageParserE

            output.write("\
                break;\n")
    output.write("""\
            default:
                assert false;
        }
    }
""")
    output.write(abstractParsers)
    output.write("\
}""")