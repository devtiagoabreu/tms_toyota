#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMScollect;
use TMSrestruct;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_STOP_HISTORY	= &TMSstr::get_str( "STOP_HISTORY"	);
my $str_PERIOD		= &TMSstr::get_str( "PERIOD"		);
my $str_LOOM_NAME	= &TMSstr::get_str( "LOOM_NAME"		);
my $str_SHOW_REPORT	= &TMSstr::get_str( "SHOW_REPORT"	);

# ----------------------------------------------------------------------------
if( &TMScollect::check_collect_date() ){  # 最近、データ収集したか

  my $html = new CGI;

  my $extend = $html->param('extend');
  if( $extend eq "on" ){  # 強引に進むか？
    &TMScollect::extend_1hour();
  }
  else{
    my $url = "stophistory.cgi?extend=on";
    print &TMScollect::need_collection_page($url);
    exit;
  }
}

# ----------------------------------------------------------------------------
if( &TMSrestruct::check_restruction() ){	# 再構築が必要の場合

  my $html = new CGI;

  my $force = $html->param('force');
  if( $force ne "on" ){	# 強引に進むか？

    my $url = "stophistory.cgi?force=on";
    print &TMSrestruct::need_restruction_page($url);
    exit;
  }
}
# ----------------------------------------------------------------------------

my $tbl_width = 630;
my $menu_color = "#426AB3";
my $body_color = "#E1E2F2";

my $loom_list = '../../tmsdata/index/history_loom.txt';

my $colspan = 2;

my $title = $str_STOP_HISTORY;
my $cgifile = 'stophistory2.cgi';
my $submit_button = $str_SHOW_REPORT;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".

	"<script language=JavaScript>\n".
	"<!--\n".
#	"  var submit_disflg = 0;\n".
#	"  function disable_submit() {\n".
#	"    document.fminput.submit.disabled = true;\n".
#	"    if(submit_disflg==0){\n".
#	"      submit_disflg = 1;\n".
#	"      return true;\n".
#	"    }else{\n".
#	"      return false;\n".
#	"    }\n".
#	"  }\n".
	"//-->\n".
	"</script>\n".

	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang).

#	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".
	"<table border=0 width=$tbl_width><tr align=center><td><font size=+2><B>$title</B></font></td></tr></table>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".

	"<tr align=center bgcolor=$menu_color>\n".
	"<th width = 50%><font size=+1 color=white>$str_PERIOD</font></th>\n".
	"<th><font size=+1 color=white>$str_LOOM_NAME</font></th>\n".
	"</tr>\n".

	"<tr align=center bgcolor=$body_color>\n".

	"<td>\n".
	"<select name=\"date\" size=20 multiple>\n";
if( open(FILE,'< ../../tmsdata/index/history_date.txt') ){
  my $selected = " selected";  # １行目は選択
  while( <FILE> ){
    $_ =~ s/\n$//;
    my @data = split(/ /,$_);
    my $value = $data[0];
    my @s = split(/\./,$data[0]);
    my $name = "$s[0]/$s[1]/$s[2]";
    my $style = "";
    if(    $data[1] == 6 ){ $style = " style=\"color=blue\""; }
    elsif( $data[1] == 0 ){ $style = " style=\"color=red\"" ; }
    print "<option value=\"$value\"$style$selected>$name</option>\n";
    $selected = "";  # ２行目以降は未選択
  }
  close(FILE);
}
print	"</select>\n".
	"</td>\n";

print	"<td><select name=\"loom\" size=20>\n";

if( open(FILE,"< $loom_list") ){
  my $selected = " selected";  # １行目は選択
  while( <FILE> ){
    my $name = $_;
    $name =~ s/\n$//;
    print "<option value=\"$name\"$selected>$name</option>\n";
    $selected = "";  # ２行目以降は未選択
  }
  close(FILE);
}
print	"</select><br>\n".
	"</td>\n".

	"</tr>\n".

	"<tr><td colspan=$colspan align=center bgcolor=$body_color>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".

	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
