#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSrestruct;
use TMSselitem;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SELECT_BY_LOOM	= &TMSstr::get_str( "SELECT_BY_LOOM"	);
my $str_SELECT_BY_STYLE	= &TMSstr::get_str( "SELECT_BY_STYLE"	);
my $str_PERIOD		= &TMSstr::get_str( "PERIOD"		);
my $str_SELECT_ALL	= &TMSstr::get_str( "SELECT_ALL"	);
my $str_SHOW_REPORT	= &TMSstr::get_str( "SHOW_REPORT"	);
my $str_SHIFT		= &TMSstr::get_str( "SHIFT"		);
my $str_DATE		= &TMSstr::get_str( "DATE"		);
my $str_WEEK		= &TMSstr::get_str( "WEEK"		);
my $str_MONTH		= &TMSstr::get_str( "MONTH"		);

my $str_SERVICE_REPORT	= &TMSstr::get_str( "SERVICE_REPORT"	);

my $html = new CGI;

my $mode = $html->param('mode');
my $period = $html->param('period');
if( $period eq "" ){
 # (補足)このレポートでは、メインメニューで初期値shift固定にしているので、
 #       通常ここの処理は走らない。
 $period = &TMSselitem::get_value_of_period();
}

# ----------------------------------------------------------------------------
if( &TMSrestruct::check_restruction() ){  # 再構築が必要の場合

  my $force = $html->param('force');
  if( $force ne "on" ){	# 強引に進むか？

    my $url = "select_s2.cgi?mode=$mode&period=$period&force=on";
    print &TMSrestruct::need_restruction_page($url);
    exit;
  }
}
# ----------------------------------------------------------------------------

my $tbl_width = 630;
my $menu_color = "#426AB3";
my $body_color = "#E1E2F2";

my $loom_list;
my $style_list;
if( $period eq 'shift' ){
  $loom_list  = '../../tmsdata/index/loom_s.txt';
  $style_list = '../../tmsdata/index/style_s.txt';
}
elsif( $period eq 'date' ){
  $loom_list  = '../../tmsdata/index/loom_d.txt';
  $style_list = '../../tmsdata/index/style_d.txt';
}
elsif( $period eq 'week' ){
  $loom_list  = '../../tmsdata/index/loom_w.txt';
  $style_list = '../../tmsdata/index/style_w.txt';
}
elsif( $period eq 'month' ){
  $loom_list  = '../../tmsdata/index/loom_m.txt';
  $style_list = '../../tmsdata/index/style_m.txt';
}

my $sel_shift = 1;
my $colspan = 3;

my $title = '';
my $cgifile = '';
my $submit_button = '';

if( $mode eq 'svsreport' ){
	$title = $str_SERVICE_REPORT;
	$cgifile = 'svsreport.cgi';
	$submit_button = $str_SHOW_REPORT;
}


print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function mode_loom() {\n".
	"    document.fminput.all_style.checked = false;\n".
	"    len = document.fminput.style.length;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.style.options[i].selected = false;\n".
	"    }\n".
	"  }\n".
	"  function sel_loom() {\n".
	"    document.fminput.sel_mode[0].checked = true;\n".
	"    document.fminput.all_loom.checked    = false;\n".
	"    document.fminput.all_style.checked   = false;\n".
	"    len = document.fminput.style.length\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.style.options[i].selected = false;\n".
	"    }\n".
	"  }\n".
	"  function sel_all_loom() {\n".
	"    document.fminput.sel_mode[0].checked = true;\n".
	"    document.fminput.all_style.checked   = false;\n".
	"    len = document.fminput.style.length;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.style.options[i].selected = false;\n".
	"    }\n".
	"    len = document.fminput.loom.length;\n".
	"    val = document.fminput.all_loom.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.loom.options[i].selected = val;\n".
	"    }\n".
	"  }\n".
	"  function mode_style() {\n".
	"    document.fminput.all_loom.checked = false;\n".
	"    len = document.fminput.loom.length\n".
	"    for (i = 0; i < document.fminput.loom.length; i ++) {\n".
	"      document.fminput.loom.options[i].selected = false;\n".
	"    }\n".
	"  }\n".
	"  function sel_style() {\n".
	"    document.fminput.sel_mode[1].checked = true;\n".
	"    document.fminput.all_style.checked   = false;\n".
	"    document.fminput.all_loom.checked    = false;\n".
	"    len = document.fminput.loom.length;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.loom.options[i].selected = false;\n".
	"    }\n".
	"  }\n".
	"  function sel_all_style() {\n".
	"    document.fminput.all_loom.checked    = false;\n".
	"    document.fminput.sel_mode[1].checked = true;\n".
	"    len = document.fminput.loom.length;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.loom.options[i].selected = false;\n".
	"    }\n".
	"    len = document.fminput.style.length;\n".
	"    val = document.fminput.all_style.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.style.options[i].selected = val;\n".
	"    }\n".
	"  }\n".
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
	"  function select_period(period) {\n".
	"    location.href = \"select_s2.cgi?mode=$mode&period=\" + period;\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang).

#	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
	"<form name=\"fminput\" action=\"$cgifile\" method=POST>\n".
	"<table width=$tbl_width><tr align=center><td><font size=+2><B>$title</B></font></td></tr></table>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n";

if( $sel_shift ){
  print	"<th><font size=+1 color=white>$str_PERIOD</font></th>\n";
}

print	"<th><input type=radio name=\"sel_mode\" value=\"loom\" checked onClick=\"mode_loom()\"><font size=+1 color=white>&nbsp;$str_SELECT_BY_LOOM</font></th>\n".
	"<th><input type=radio name=\"sel_mode\" value=\"style\" onClick=\"mode_style()\"><font size=+1 color=white>&nbsp;$str_SELECT_BY_STYLE</font></th>\n".
	"</tr>\n".

	"<tr align=center bgcolor=$body_color>\n";

if( $sel_shift ){
  my $checked_shift = ""; if( $period eq 'shift' ){ $checked_shift = 'checked'; }
  my $checked_date  = ""; if( $period eq 'date'  ){ $checked_date  = 'checked'; }
  my $checked_week  = ""; if( $period eq 'week'  ){ $checked_week  = 'checked'; }
  my $checked_month = ""; if( $period eq 'month' ){ $checked_month = 'checked'; }

  print	"<td width=33%>\n".
	"<table border=0 width=100%><tr>\n".
	"<td valign=top align=right>\n".
	"<table><tr><td>\n".
	"<BR>\n".
	"<NOBR>\n".
	"<input type=radio name=\"period\" value=\"shift\" $checked_shift onClick=\"select_period('shift')\"><B>$str_SHIFT</B><BR>\n".
	"<input type=radio name=\"period\" value=\"date\" $checked_date onClick=\"select_period('date')\"><B>$str_DATE</B><BR>\n".
	"<input type=radio name=\"period\" value=\"week\" $checked_week onClick=\"select_period('week')\"><B>$str_WEEK</B><BR>\n".
	"<input type=radio name=\"period\" value=\"month\" $checked_month onClick=\"select_period('month')\"><B>$str_MONTH</B><BR>\n".
	"</NOBR>\n".
	"</td></tr></table>\n".
	"</td>\n".
	"<td align=center>\n".
	"<select name=\"shift\" size=20 multiple>\n";

  if( $period eq 'shift' ){
    my @shift_id = &TMScommon::get_shift_id();
    if( open(FILE,'< ../../tmsdata/index/shift_shift.txt') ){
      my $selected = " selected";
      while( <FILE> ){
        $_ =~ s/\n$//;
        my @data = split(/ /,$_);
        my $value = $data[0];
        my @s = split(/\./,$data[0]);
        my $name = "$s[0]/$s[1]/$s[2].$shift_id[$s[3]]";
        my $style = "";
        if(    $data[1] == 6 ){ $style = " style=\"color=blue\""; }
        elsif( $data[1] == 0 ){ $style = " style=\"color=red\"" ; }
        print "<option value=\"$value\"$style$selected>$name</option>\n";
        $selected = "";
      }
      close(FILE);
    }
  }
  elsif( $period eq 'date' ){
    if( open(FILE,'< ../../tmsdata/index/shift_date.txt') ){
      my $selected = " selected";
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
        $selected = "";
      }
      close(FILE);
    }
  }
  elsif( $period eq 'week' ){
    if( open(FILE,'< ../../tmsdata/index/shift_week.txt') ){
      my $selected = " selected";
      while( <FILE> ){
        $_ =~ s/\n$//;
        my $value = $_;
        my @s = split(/\./,$_);
        my $name = "$s[0]/$s[1]/$s[2]";
        print "<option value=\"$value\"$selected>$name</option>\n";
        $selected = "";
      }
      close(FILE);
    }
  }
  elsif( $period eq 'month' ){
    if( open(FILE,'< ../../tmsdata/index/shift_month.txt') ){
      my $selected = " selected";
      while( <FILE> ){
        $_ =~ s/\n$//;
        my $value = $_;
        my @s = split(/\./,$_);
        my $name = "$s[0]/$s[1]";
        print "<option value=\"$value\"$selected>$name</option>\n";
        $selected = "";
      }
      close(FILE);
    }
  }

  print	"</select>\n".
	"</td></tr></table>\n".
	"</td>\n";
}

print	"<td><select name=\"loom\" size=18 multiple onFocus=\"sel_loom()\">\n";

if( open(FILE,"< $loom_list") ){
  my $sel_flg = 1;
  while( <FILE> ){
    my $name = $_;
    $name =~ s/\n$//;
    if( $sel_flg ){ $sel_flg = 0; print "<option value=\"$name\" selected>$name</option>\n"; }
    else{ print "<option value=\"$name\">$name</option>\n"; }
  }
  close(FILE);
}
print	"</select><br>\n".
	"<input type=CHECKBOX name=\"all_loom\" onClick=\"sel_all_loom()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td>\n".
	"<td>\n".
	"<select name=\"style\" size=18 multiple onFocus=\"sel_style()\">\n";

if( open(FILE,"< $style_list") ){
  while( <FILE> ){
    my $name = $_;
    $name =~ s/\n$//;
    print "<option value=\"$name\">$name</option>\n";
  }
  close(FILE);
}
print	"</select><br>\n".
	"<input type=CHECKBOX name=\"all_style\" OnClick=\"sel_all_style()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td>\n".

	"</tr>\n".
	"<tr><td colspan=$colspan align=center bgcolor=$body_color>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
