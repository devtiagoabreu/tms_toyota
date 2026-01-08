#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSjavascript;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SHIFT_SCHEDULE_SETTING	= &TMSstr::get_str( 'SHIFT_SCHEDULE_SETTING'	);

my $str_INVALID_INPUT_VALUE	= &TMSstr::get_str( 'INVALID_INPUT_VALUE'	);
my $str_UPDATE_SETTING		= &TMSstr::get_str( 'UPDATE_SETTING'		);
my $str_UPDATE_OK		= &TMSstr::get_str( 'UPDATE_OK'			);

my $str_SUNDAY			= &TMSstr::get_str( "SUNDAY"	);
my $str_MONDAY			= &TMSstr::get_str( "MONDAY"	);
my $str_TUESDAY			= &TMSstr::get_str( "TUESDAY"	);
my $str_WEDNESDAY		= &TMSstr::get_str( "WEDNESDAY"	);
my $str_THURSDAY		= &TMSstr::get_str( "THURSDAY"	);
my $str_FRIDAY			= &TMSstr::get_str( "FRIDAY"	);
my $str_SATDAY			= &TMSstr::get_str( "SATDAY"	);

my $str_SCANNER			= &TMSstr::get_str( 'SCANNER'		);
my $str_SHIFT_SCHEDULE		= &TMSstr::get_str( 'SHIFT_SCHEDULE'	);
my $str_SIMPLE_SETTING		= &TMSstr::get_str( 'SIMPLE_SETTING'	);
my $str_DETAIL_SETTING		= &TMSstr::get_str( 'DETAIL_SETTING'	);
my $str_SHIFT_NUMBER		= &TMSstr::get_str( 'SHIFT_NUMBER'	);

################################################################

## 初期値
my $shift_schedule_is_week = 0;  # false
my @shift_schedule_simple = (3, "08","00", "16","00", "23","59", "","", "","");
my @shift_schedule_week;
for( my $i=0; $i<=6; $i++ ){
  @{$shift_schedule_week[$i]} = (3, "08","00", "16","00", "23","59", "","", "","");
}

## 設定ファイル読み出し
my @system_set = &TMSscanner::get_system_set();

foreach( @system_set ){
  if( m/^shift_schedule_is_week\s+([0-1])$/ ){
    $shift_schedule_is_week = $1;
  }
  elsif( m/^shift_schedule_simple\s+([0-5])\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)$/ ){
    my @data = ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11);
    foreach my $val (@data){
      if( $val == -1 ){ $val = ""; }  # -1 は表示しない
    }
    @shift_schedule_simple = @data;
  }
  elsif( m/^shift_schedule_week\s+([0-6])\s+([0-5])\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)\s+([-0-9]+):([-0-9]+)$/ ){
    my @data = ($2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12);
    foreach my $val (@data){
      if( $val == -1 ){ $val = ""; }  # -1 は表示しない
    }
    @{$shift_schedule_week[$1]} = @data;
  }
}

################################################################

my $tbl_width = 630;

my $title = $str_SHIFT_SCHEDULE_SETTING;
my $cgifile = 'shiftset2.cgi';
my $menu_color = '#ED1C24';
my $body_color = '#FDE1D4';
my $submit_button = $str_UPDATE_SETTING;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n";

print &TMSjavascript::checkNumber();

print	"  function checkShift(obj) {\n".
	"    var hhmm = new Array(5);\n".
	"    i=0;\n".
	"    while( i < obj[0].value ){\n".
	"      if( ! checkNumber(obj[i*2+1], 0, 23) ){ return false; }\n".
	"      if( ! checkNumber(obj[i*2+2], 0, 59) ){ return false; }\n".
	"      hh = parseInt(obj[i*2+1].value,10);\n".
	"      mm = parseInt(obj[i*2+2].value,10);\n".
	"      hhmm[i] = (hh *100) + mm;\n".
	"      if( hh < 10 ){ hh = \"0\" + hh; }\n".
	"      if( mm < 10 ){ mm = \"0\" + mm; }\n".
	"      obj[i*2+1].value = hh;\n".
	"      obj[i*2+2].value = mm;\n".
	"      ++i;\n".
	"    }\n".
	"    while( i < 5 ){\n".
	"      obj[i*2+1].value = \"\";\n".
	"      obj[i*2+2].value = \"\";\n".
	"      ++i;\n".
	"    }\n".
	"    for( i=0; i+1<obj[0].value; i++ ){\n".
	"      if( hhmm[i] >= hhmm[i+1] ){\n".
	"        alert(\"$str_INVALID_INPUT_VALUE\");\n".
	"        obj[(i+1)*2+1].focus();\n".
	"        obj[(i+1)*2+1].select();\n".
	"        return false;\n".
	"      }\n".
	"    }\n".
	"    return true;\n".
	"  }\n\n".

	"  function checkSubmit(aForm) {\n".
	"    if( ! checkShift(aForm.simple) ){ return false; }\n".
	"    if( ! checkShift(aForm.week1) ){ return false; }\n".
	"    if( ! checkShift(aForm.week2) ){ return false; }\n".
	"    if( ! checkShift(aForm.week3) ){ return false; }\n".
	"    if( ! checkShift(aForm.week4) ){ return false; }\n".
	"    if( ! checkShift(aForm.week5) ){ return false; }\n".
	"    if( ! checkShift(aForm.week6) ){ return false; }\n".
	"    if( ! checkShift(aForm.week0) ){ return false; }\n".
	"    return confirm(\"$str_UPDATE_OK\");\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n";

print	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return checkSubmit(this);\">\n".
	"<table width=$tbl_width><tr><th><font size=+2>$title</font></th></tr></table>\n";

print	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th colspan=2><font size=+2 color=white>$str_SHIFT_SCHEDULE</font></th>\n".
	"<tr valign=top align=center bgcolor=$body_color><td>\n";

my @checked = ("","");
if( $shift_schedule_is_week == 0 ){ $checked[0] = "checked"; }
else{                               $checked[1] = "checked"; }

#### 簡易設定 ####
print	"<input type=radio name=\"is_week\" value=\"0\" $checked[0]>$str_SIMPLE_SETTING<BR><BR><BR>\n";

&print_schedule_table("simple", \@shift_schedule_simple);

print	"</td>\n".
	"<td>\n";

#### 詳細設定 ####
print	"<input type=radio name=\"is_week\" value=\"1\" $checked[1]>$str_DETAIL_SETTING<BR><BR>\n";

print	"<TABLE>\n".
	"<TR align=center><TD>\n".
	"<B>$str_MONDAY</B><BR>\n";
&print_schedule_table("week1", $shift_schedule_week[1]);
print	"</TD><TD>\n".
	"<B>$str_TUESDAY</B><BR>\n";
&print_schedule_table("week2", $shift_schedule_week[2]);
print	"</TD><TD>\n".
	"<B>$str_WEDNESDAY</B><BR>\n";
&print_schedule_table("week3", $shift_schedule_week[3]);
print	"</TD></TR>\n";

print	"<TR align=center><TD>\n".
	"<B>$str_THURSDAY</B><BR>\n";
&print_schedule_table("week4", $shift_schedule_week[4]);
print	"</TD><TD>\n".
	"<B>$str_FRIDAY</B><BR>\n";
&print_schedule_table("week5", $shift_schedule_week[5]);
print	"</TD><TD>\n".
	"<B>$str_SATDAY</B><BR>\n";
&print_schedule_table("week6", $shift_schedule_week[6]);
print	"</TD></TR>\n";

print	"<TR align=center><TD>\n".
	"<B>$str_SUNDAY</B><BR>\n";
&print_schedule_table("week0", $shift_schedule_week[0]);
print	"</TD><TD>\n".
	"</TD></TR>\n".
	"</TABLE>\n";

print	"</td></tr>\n";

#### submit ボタン ####
print	"<tr><td align=center bgcolor=$body_color colspan=2>\n".

	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

##############################################################################################

sub print_schedule_table
{
  my($name,$r_schedule) = @_;

  print	"<TABLE border=1 cellspacing=0 cellpadding=5>\n".
	"<TR align=center><TD nowrap>$str_SHIFT_NUMBER\n".
	"<SELECT name=\"$name\">\n";

  for( my $n=1; $n<=5; $n++ ){
    if( $n == $$r_schedule[0] ){ print "<option value=$n selected>$n</option>\n"; }
    else{                        print "<option value=$n>$n</option>\n"; }
  }

  print "</SELECT></TD></TR>\n".
	"<TR><TD>\n".
	"<TABLE>\n";

  my @shift = ("A","B","C","D","E");
  for( my $i=0; $i<5; $i++ ){
    my $j = 1 + ($i * 2);
    print "<TR align=center><TD>$shift[$i]</TD>".
          "<TD nowrap><input type=text name=\"$name\" value=\"$$r_schedule[$j]\" size=3>".
          " : <input type=text name=\"$name\" value=\"$$r_schedule[$j+1]\" size=3></TD></TR>\n";
  }
  print "</TABLE>\n".
	"</TD></TR>\n".
	"</TABLE>\n";
}
