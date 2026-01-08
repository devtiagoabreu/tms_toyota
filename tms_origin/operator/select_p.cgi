#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMScollect;
use TMSrestruct;
use TMSselitem;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_PRODUCTION_GRAPH	= &TMSstr::get_str( "PRODUCTION_GRAPH"	);
my $str_EFFICIENCY_GRAPH	= &TMSstr::get_str( "EFFICIENCY_GRAPH"	);
my $str_OPERATOR_REPORT		= &TMSstr::get_str( "OPERATOR_REPORT"	);
my $str_OPERATOR		= &TMSstr::get_str( "OPERATOR"		);
my $str_PERIOD			= &TMSstr::get_str( "PERIOD"		);
my $str_SELECT_ALL		= &TMSstr::get_str( "SELECT_ALL"	);
my $str_SHOW_GRAPH		= &TMSstr::get_str( "SHOW_GRAPH"	);
my $str_SHOW_REPORT		= &TMSstr::get_str( "SHOW_REPORT"	);
my $str_DATE			= &TMSstr::get_str( "DATE"		);
my $str_WEEK			= &TMSstr::get_str( "WEEK"		);
my $str_MONTH			= &TMSstr::get_str( "MONTH"		);

my $html = new CGI;
my $mode = $html->param('mode');
my $period = $html->param('period');
if( $period eq "" ){
 $period = &TMSselitem::get_value_of_period();
 if( $period eq 'shift' ){ $period = 'date'; }
}

# ----------------------------------------------------------------------------
if( &TMScollect::check_collect_date() ){  # 最近、データ収集したか

  my $extend = $html->param('extend');
  if( $extend eq "on" ){  # 強引に進むか？
    &TMScollect::extend_1hour();
  }
  else{
    my $url = "select_p.cgi?mode=$mode&period=$period&extend=on";
    print &TMScollect::need_collection_page($url);
    exit;
  }
}

# ----------------------------------------------------------------------------
if( &TMSrestruct::check_restruction() ){	# 再構築が必要の場合

  my $force = $html->param('force');
  if( $force ne "on" ){	# 強引に進むか？

    my $url = "select_p.cgi?mode=$mode&period=$period&force=on";
    print &TMSrestruct::need_restruction_page($url);
    exit;
  }
}
# ----------------------------------------------------------------------------

my $tbl_width = 630;
my $menu_color = '#00A77E';
my $body_color = '#DCEFE7';

my $operator_list;
if(    $period eq 'date' ){
  $operator_list = '../../tmsdata/index/operator_d.txt';
}
elsif( $period eq 'week' ){
  $operator_list = '../../tmsdata/index/operator_w.txt';
}
elsif( $period eq 'month' ){
  $operator_list = '../../tmsdata/index/operator_m.txt';
}

my $title = '';
my $cgifile = '';
my $submit_button = '';

if( $mode eq 'shiftreport' ){
	$title = $str_OPERATOR_REPORT;
	$cgifile = 'shiftreport_p.cgi';
	$submit_button = $str_SHOW_REPORT
}
elsif( $mode eq 'production' ){
	$title = $str_PRODUCTION_GRAPH;
	$cgifile = 'production_p.cgi';
	$submit_button = $str_SHOW_GRAPH
}
elsif( $mode eq 'efficiency' ){
	$title = $str_EFFICIENCY_GRAPH;
	$cgifile = 'efficiency_p.cgi';
	$submit_button = $str_SHOW_GRAPH
}


print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function sel_all_operator() {\n".
	"    len = document.fminput.operator.length\n".
	"    val = document.fminput.all_operator.checked;\n".
	"    for (i = 0; i < len; i++) {\n".
	"      document.fminput.operator.options[i].selected = val;\n".
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
	"    location.href = \"select_p.cgi?mode=$mode&period=\" + period;\n".
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
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+1 color=white>$str_PERIOD</font></th>\n".
	"<th><font size=+1 color=white>$str_OPERATOR</font></th>\n".
	"</tr>\n".

	"<tr align=center bgcolor=$body_color>\n";

my $checked_date  = ""; if( $period eq 'date'  ){ $checked_date  = 'checked'; }
my $checked_week  = ""; if( $period eq 'week'  ){ $checked_week  = 'checked'; }
my $checked_month = ""; if( $period eq 'month' ){ $checked_month = 'checked'; }

print	"<td width=40%>\n".
	"<table border=0 width=100%><tr>\n".
	"<td valign=top align=right>\n".
	"<table><tr><td>\n".
	"<BR>\n".
	"<NOBR>\n".
	"<input type=radio name=\"period\" value=\"date\" $checked_date onClick=\"select_period('date')\"><B>$str_DATE</B><BR>\n".
	"<input type=radio name=\"period\" value=\"week\" $checked_week onClick=\"select_period('week')\"><B>$str_WEEK</B><BR>\n".
	"<input type=radio name=\"period\" value=\"month\" $checked_month onClick=\"select_period('month')\"><B>$str_MONTH</B><BR>\n".
	"</NOBR>\n".
	"</td></tr></table>\n".
	"</td>\n".
	"<td align=center>\n".
	"<select name=\"day\" size=20 multiple>\n";

if( $period eq 'date' ){
  if( open(FILE,'< ../../tmsdata/index/opedata_date.txt') ){
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
  if( open(FILE,'< ../../tmsdata/index/opedata_week.txt') ){
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
  if( open(FILE,'< ../../tmsdata/index/opedata_month.txt') ){
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
	"</td>\n".
	"<td><select name=\"operator\" size=18 multiple onFocus=\"javascript:document.fminput.all_operator.checked=false\">\n";

if( open(FILE,"< $operator_list") ){
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
	"<input type=CHECKBOX name=\"all_operator\" onClick=\"sel_all_operator()\"><font size=+1><B>$str_SELECT_ALL</B></font>\n".
	"</td></tr>\n".
	"<tr><td colspan=2 align=center bgcolor=$body_color>\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\">\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
