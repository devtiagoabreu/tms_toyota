#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSipset;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_LOOM_CLOCK_SETTING	= &TMSstr::get_str( "LOOM_CLOCK_SETTING"	);
my $str_SELECT_ALL		= &TMSstr::get_str( "SELECT_ALL"		);
my $str_ENTER			= &TMSstr::get_str( "ENTER"			);
my $str_TARGET_DATE		= &TMSstr::get_str( "TARGET_DATE"		);
my $str_SCANNER			= &TMSstr::get_str( 'SCANNER'			);


# エラー画面表示があるので、html出力の前に処理する事！
my @scan_ip = &TMSscanner::get_scan_ip();

my $tbl_width = 630;
my $menu_color = '#FDB913';
my $body_color = '#FFF2DD';

my $cgifile = 'setclock2.cgi';
my $title = $str_LOOM_CLOCK_SETTING;
my $submit_button = $str_ENTER;

# Webサーバー側の時刻を表示（リモート参照対応）

my $clock = "";
{
  my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
  $clock = sprintf("%d/%d/%d,%d:%d:%d",($year+1900),($mon+1),$mday,$hour,$min,$sec);
}

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  var now = new Date(\"$clock\");\n".
	"  function ShowPcClock() {\n".
	"    var year  = now.getYear();\n".
	"    var month = now.getMonth()+1;\n".
	"    var date  = now.getDate();\n".
	"    var hour  = now.getHours();\n".
	"    var min   = now.getMinutes();\n".
	"    var sec   = now.getSeconds();\n".
	"    if( hour < 10 ){ hour = \"0\" + hour; }\n".
	"    if( min  < 10 ){ min  = \"0\" + min;  }\n".
	"    if( sec  < 10 ){ sec  = \"0\" + sec;  }\n".
	"    document.fminput.clock.value = '  '+year+'/'+month+'/'+date+'  '+hour+':'+min+':'+sec;\n".
	"    now.setTime(now.getTime()+1000);\n".	# for Next
	"    setTimeout(\"ShowPcClock()\",1000);\n".
	"  }\n".
	"  function sel_loom() {\n".
	"    document.fminput.all_loom.checked = false;\n".
	"  }\n".
	"  function sel_all_loom() {\n".
	"    len = document.fminput.loom.length;\n".
	"    val = document.fminput.all_loom.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.loom.options[i].selected = val;\n".
	"    }\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2 onLoad=\"ShowPcClock()\"><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>\n".

	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".

	"<tr align=center bgcolor=$body_color>\n".
	"<td>\n".
	"<label><B>$str_TARGET_DATE&nbsp;:&nbsp;</B></label><input type=text name=clock size=28>\n".
	"<br><br>\n".
	"<table><tr>\n";

my @ip_list = &TMSipset::get_all_ip_list();
# JAT710 がある場合のみ
if( $#ip_list >= 0 ){
  my @name_list = ();
  &TMSipset::get_name_ip_list( \@name_list, \@ip_list );

  print "<td>\n".
	"<select name=\"loom\" size=16 multiple onFocus=\"sel_loom()\">\n";

  for( my $i=0; $i<=$#name_list; $i++ ){
    my $name = $name_list[$i];
    my $ip   = $ip_list[$i];
    if( $ip eq $name ){
      print "<option value=\"$ip\">$name</option>\n";
    } else{
      print "<option value=\"$ip\">$name ($ip)</option>\n";
    }
  }
  print	"</select><br>\n".
	"<input type=CHECKBOX name=\"all_loom\" OnClick=\"sel_all_loom()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td>\n";
}

# スキャナーがある場合のみ
if( $#scan_ip >= 0 ){
  my @disabled = ("","","","","");
  if( ! defined($scan_ip[0]) ){ $disabled[0] = "disabled"; }
  if( ! defined($scan_ip[1]) ){ $disabled[1] = "disabled"; }
  if( ! defined($scan_ip[2]) ){ $disabled[2] = "disabled"; }
  if( ! defined($scan_ip[3]) ){ $disabled[3] = "disabled"; }
  if( ! defined($scan_ip[4]) ){ $disabled[4] = "disabled"; }

  if( $#ip_list >= 0 ){
    print "<td width=30></td>\n";
  }
  print "<td>\n";
  print "<input type=CHECKBOX name=\"scanner\" value=\"1\" $disabled[0]><B>$str_SCANNER 1</B><br>\n";
  print "<input type=CHECKBOX name=\"scanner\" value=\"2\" $disabled[1]><B>$str_SCANNER 2</B><br>\n";
  print "<input type=CHECKBOX name=\"scanner\" value=\"3\" $disabled[2]><B>$str_SCANNER 3</B><br>\n";
  print "<input type=CHECKBOX name=\"scanner\" value=\"4\" $disabled[3]><B>$str_SCANNER 4</B><br>\n";
  print "<input type=CHECKBOX name=\"scanner\" value=\"5\" $disabled[4]><B>$str_SCANNER 5</B><br>\n";
  print "<br></td>\n";
}
print	"</tr></table>\n";

print	"</td>\n".
	"</tr>\n".
	"<tr><td align=center bgcolor=$body_color>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
