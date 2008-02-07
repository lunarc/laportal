#
# Security module
#
# Copyright (C) 2006-2008 Jonas Lindemann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#

"""Security module

This module contains routines for handling bad user input, in the form
of a mixin class, that can be added to WebKit page classes."""

import re

class FieldValidationMixin:
        """Field validation mixin class
        
        This class contains routines for validating different kinds of user input."""

        def safeString(self, inputString):
                """Removes unwanted characters from the inputString parameter. The
                routine removes linebreaks."""
                cleanString = re.sub("""[.\\\;<>\*\|`&$!#()\[\]\{\}:'"/\\n]+""","", inputString)
                return cleanString

        def safeMultiString(self, inputString):
                """Removes unwanted characters from the inputString parameter. The
                routine keeps linebreaks."""
                cleanString = re.sub("""[.\\\;<>\*\|`&$!#()\[\]\{\}:'"/]+""","", inputString)
                return cleanString

        def safeStringWidthDot(self, inputString):
                """Removes unwanted characters from the inputString parameter. The
                routine removes linebreaks and keeps dots."""
                cleanString = re.sub("""[\\\;<>\*\|`&$!#()\[\]\{\}:'"/\\n]+""","", inputString)
                return cleanString

        def safeStringWithDot(self, inputString):
                """Removes unwanted characters from the inputString parameter. The
                routine removes linebreaks and keeps dots."""
                cleanString = re.sub("""[\\\;<>\*\|`&$!#()\[\]\{\}:'"/\\n]+""","", inputString)
                return cleanString

        def safeMultiStringWidthDot(self, inputString):
                """Removes unwanted characters from the inputString parameter. The
                routine keeps linebreaks and dots."""
                cleanString = re.sub("""[\\\;<>\*\|`&$!#()\[\]\{\}:'"/]+""","", inputString)
                return cleanString
        
        def safeMultiStringWithDot(self, inputString):
                """Removes unwanted characters from the inputString parameter. The
                routine keeps linebreaks and dots."""
                cleanString = re.sub("""[\\\;<>\*\|`&$!#()\[\]\{\}:'"/]+""","", inputString)
                return cleanString

        def safeURLString(self, inputString):
                """Removes unwanted characters from the inputString parameter. The
                routine preserves characters used in a valid URL."""
                cleanString = re.sub("""[\\\;<>\*\|`&$!#()\[\]\{\}'"\\n]+""","", inputString)
                return cleanString

        def getField(self, request, fieldName):
                """Retrieve field with dangerous characters removed."""
                if request.hasValue(fieldName):
                        return self.safeStringWidthDot(request.field(fieldName))
                else:
                        return None
                
        def getURLField(self, request, fieldName):
                """Retrieve field with dangerous characters removed."""
                if request.hasValue(fieldName):
                        return self.safeURLString(request.field(fieldName))
                else:
                        return None

        def getMultiField(self, request, fieldName):
                """Retrieve field with dangerous characters removed."""
                if request.hasValue(fieldName):
                        return self.safeMultiStringWidthDot(request.field(fieldName))
                else:
                        return None

        def getFileField(self, request, fieldName, alternateFieldName):
                """Retrieve file name from a file field."""

                if request.hasField(fieldName):
                        f = request.field(fieldName)
                else:
                        filename = ""
                        return

                filename = ""

                try:
                        filename = f.filename
                except:
                        filename = request.field(alternateFieldName)

                return filename


        def getString(self, request, fieldName):
                """Retrieve a string from fieldname."""
                return self.getField(request, fieldName)
        
        def getStringNoDoubleDot(self, request, fieldName):
                """Retrieve a string from fieldName, removing any double dots."""
                firstPass = self.getString(request, fieldName)
                return firstPass.replace("..", "")

        def getMultiString(self, request, fieldName):
                """Retrieve a multistring from fieldName."""
                multiString = self.getMultiField(request, fieldName)
                return multiString.split("\r\n")
        
        def getURLString(self, request, fieldName):
                """Retrieve a URL string from fieldName."""
                return self.getURLField(request, fieldName)
        
        def getHostname(self, request, fieldName):
                """Retrieve a hostname from fieldName."""
                valueString = self.getField(request, fieldName)

                if valueString!=None:
                        m1 = re.match("\s*\w+\.\w+\.\w+\.\w+\s*", valueString)
                        m2 = re.match("\s*\w+\.\w+\.\w+\s*", valueString)
                        m3 = re.match("\s*\w+\.\w+\s*", valueString)
                        m4 = re.match("\s*\w+\s*", valueString)
                        
                        if m1!=None:
                                return valueString.strip()
                        
                        if m2!=None:
                                return valueString.strip()
                        
                        if m3!=None:
                                return valueString.strip()
                        
                        if m4!=None:
                                return valueString.strip()
                        
                        return None
                else:
                        return None

        def getEmail(self, request, fieldName):
                """Retrieve a email from fieldName."""
                return self.getField(request, fieldName)

        def getInt(self, request, fieldName):
                """Retrieve an integer from fieldName."""
                valueString = self.getField(request, fieldName)
                value = -1

                try:
                        value = float(valueString)
                        value = int(value)
                except:
                        return None

                return value

        def getFloat(self, request, fieldName):
                """Retrieve an float from a field."""
                valueString = self.getField(request, fieldName)
                value = 0.0

                try:
                        value = float(valueString)
                except:
                        return None

                return value
