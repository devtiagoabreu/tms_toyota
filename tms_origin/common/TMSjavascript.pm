package TMSjavascript;

###################################################################################################
#
# TMSjavascript.pm
#
###################################################################################################

use strict;

use TMSstr;

###################################################################################################

sub checkName
{
  my $str_INVALID_INPUT_VALUE = &TMSstr::get_str( 'INVALID_INPUT_VALUE' );
  my $str_ALPHANUMERIC_ONLY   = &TMSstr::get_str( 'ALPHANUMERIC_ONLY' );

  return "  function checkName(obj) {\n".
	 "    if( obj.value.length == 0 ){ return 0; }\n".
	 "    obj.value = obj.value.replace(/^\\s+/,\"\");\n".   # 先頭のスペース削除
	 "    obj.value = obj.value.replace(/\\s+\$/,\"\");\n".  # 末尾のスペース削除
	 "    if( obj.value.length == 0 ){ return 0; }\n".
	 "    if( obj.value.match(/[^a-zA-Z0-9_-]/) ){\n".
	 "      alert(\"$str_INVALID_INPUT_VALUE ($str_ALPHANUMERIC_ONLY)\");\n".
	 "      obj.focus();\n".
	 "      obj.select();\n".
	 "      return -1;\n".  # ERROR
	 "    }\n".
	 "    return 1;\n".  # OK
	 "  }\n\n";
}

###################################################################################################

sub checkNumber
{
  my $str_INVALID_INPUT_VALUE = &TMSstr::get_str( 'INVALID_INPUT_VALUE' );

  return "  function checkNumber(obj, min, max) {\n".
	 "    obj.value = obj.value.replace(/\\s/g,\"\");\n".  # 空白を削除
	 "    if( (obj.value.length > 0) && (! isNaN(obj.value)) ){\n".
	 "       ok = true;\n".
	 "       if( ! isNaN(min) ){\n".
	 "         if( obj.value < min ){ ok = false; }\n".
	 "       }\n".
	 "       if( ! isNaN(max) ){\n".
	 "         if( obj.value > max ){ ok = false; }\n".
	 "       }\n".
	 "       if( ok ){ return true; }\n".
	 "    }\n".
	 "    alert(\"$str_INVALID_INPUT_VALUE ( \"+ min +\" .. \" + max + \" )\");\n".
	 "    obj.focus();\n".
	 "    obj.select();\n".
	 "    return false;\n".
	 "  }\n\n";
}

###################################################################################################
1;
