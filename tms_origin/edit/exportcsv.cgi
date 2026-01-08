#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DirHandle;

use TMSstr;
use TMScommon;
use TMSdeny;
use TMScollect;
use TMSstophist;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_EXPORT_CSV_FILE		= &TMSstr::get_str( "EXPORT_CSV_FILE"		);
my $str_SHIFT_DATA		= &TMSstr::get_str( "SHIFT_DATA"		);
my $str_STOP_HISTORY		= &TMSstr::get_str( "STOP_HISTORY"		);
my $str_OPERATOR_DATA		= &TMSstr::get_str( "OPERATOR_DATA"		);
my $str_YARN_INVENTORY_FORECAST	= &TMSstr::get_str( "YARN_INVENTORY_FORECAST"	);
my $str_SELECT_ALL		= &TMSstr::get_str( "SELECT_ALL"		);
my $str_RESET_MODEIFY		= &TMSstr::get_str( "RESET_MODEIFY"		);
my $str_SELECT_EXPORT_DATA	= &TMSstr::get_str( "SELECT_EXPORT_DATA"	);
my $str_EXPORT_DATA		= &TMSstr::get_str( "EXPORT_DATA"		);

# ----------------------------------------------------------------------------
my $submit_disable = "";
if( &TMSdeny::is_demo_mode() == 1){ $submit_disable = " disabled"; }
elsif( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

# ----------------------------------------------------------------------------
if( &TMScollect::check_collect_date() ){  # 最近、データ収集したか

  my $html = new CGI;
  my $extend = $html->param('extend');
  if( $extend eq "on" ){  # 強引に進むか？
    &TMScollect::extend_1hour();
  }
  else{
    my $url = "exportcsv.cgi?extend=on";
    print &TMScollect::need_collection_page($url);
    exit;
  }
}

# ----------------------------------------------------------------------------

# シフトデータの月リスト作成
my @shift_month = ();
my $dirname = "..\\..\\tmsdata\\shift";
if( -d $dirname ){
  my $dir = new DirHandle $dirname;		# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.\d\.txt$/ ){
      my @d = split(/\./,$f,3);
      &TMScommon::entry_to_list( \@shift_month, "$d[0].$d[1]" );
    }
  }
  $dir->close;
  @shift_month = sort @shift_month;	# 配列をソートする。
}

# オペレータデータの月リスト作成
my @ope_month = ();
$dirname = "..\\..\\tmsdata\\operator";
if( -d $dirname ){
  my $dir = new DirHandle $dirname;		# ディレクトリのファイルリストを取得する
  while( my $f = $dir->read ){
    if( $f =~ m/^\d{4}\.\d{2}\.\d{2}\.txt$/ ){
      my @d = split(/\./,$f,3);
      &TMScommon::entry_to_list( \@ope_month, "$d[0].$d[1]" );
    }
  }
  $dir->close;
  @ope_month = sort @ope_month;	# 配列をソートする。
}

# 停止履歴データの月リスト作成
my @history_month = ();
my ($stophist_dir, @stophist_subdir) = &TMSstophist::get_stophist_dir();
foreach my $subdir ( @stophist_subdir ){
  my $ym = substr( $subdir, 0, 7 ); # yyyy.mmの部分を取得
  &TMScommon::entry_to_list( \@history_month, $ym );
}
@history_month = sort @history_month;	# 配列をソートする。


my $tbl_width = 630;
my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

my $title = $str_EXPORT_CSV_FILE;
my $cgifile = 'exportcsv2.cgi';
my $reset_button = $str_RESET_MODEIFY;
my $submit_button = $str_EXPORT_DATA;

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  var submit_disflg = 0;\n".
	"  function disable_submit() {\n".
	"    document.fminput.submit.disabled = true;\n".
	"    if(submit_disflg==0){\n".
	"      submit_disflg = 1;\n".
	"      return true;\n".
	"    }else{\n".
	"      return false;\n".
	"    }\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang).

	"<form name=\"fminput\" action=\"$cgifile\" method=POST onSubmit=\"return disable_submit()\">\n".
	"<table width=$tbl_width><tr align=center><td><font size=+2><B>$title</B></font></td></tr></table>\n".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".

	"<th colspan=3><font size=+1 color=white>$str_SELECT_EXPORT_DATA</font></th></tr>\n";

print	"<tr align=center bgcolor=$body_color>\n".

#--------- シフト別データ --------------------

	"<td align=center nowrap width=34%>\n".
	"<BR><font size=+1><B>$str_SHIFT_DATA</B></font><BR>\n".
	"<select name=\"shift\" size=12 multiple>\n";

for( my $i=$#shift_month; $i>=0; $i-- ){
  my $value = $shift_month[$i];
  my @s = split(/\./,$value);
  my $name = "$s[0]/$s[1]";
  print "<option value=\"$value\">$name</option>\n";
}

print	"</select><br>\n".
	"</td>\n".

#--------- 作業者別データ --------------------

	"<td align=center nowrap width=34%>\n".
	"<BR><font size=+1><B>$str_OPERATOR_DATA</B></font><BR>\n".
	"<select name=\"operator\" size=12 multiple>\n";

for( my $i=$#ope_month; $i>=0; $i-- ){
  my $value = $ope_month[$i];
  my @s = split(/\./,$value);
  my $name = "$s[0]/$s[1]";
 print "<option value=\"$value\">$name</option>\n";
}

print	"</select><br>\n".
	"</td>\n".

#--------- 停止履歴 --------------------

	"<td align=center nowrap>\n".
	"<BR><font size=+1><B>$str_STOP_HISTORY</B></font><BR>\n".
	"<select name=\"history\" size=12 multiple>\n";

for( my $i=$#history_month; $i>=0; $i-- ){
  my $value = $history_month[$i];
  my @s = split(/\./,$value);
  my $name = "$s[0]/$s[1]";
  print "<option value=\"$value\">$name</option>\n";
}

print	"</select><br>\n".
	"</td>\n".
	"</tr>\n";

#--------- 予測 --------------------

my $disabled = "";
unless( -f "..\\..\\tmsdata\\current\\current.txt" ){ $disabled = " disabled"; }

print	"<tr align=center bgcolor=$body_color>\n".
	"<td  colspan=3>\n".
	"<BR>\n".
	"<NOBR><input type=CHECKBOX name=\"forecast\" value=\"on\"$disabled><font size=+1><B>$str_YARN_INVENTORY_FORECAST</B></font></NOBR>\n".
	"<BR><BR>\n".
	"</td>\n".
	"</tr>\n".
	"<tr><td colspan=3 align=center bgcolor=$body_color>\n".
	"<input type=RESET name=\"reset\" value=\"$reset_button\">\n".
	"<input type=SUBMIT name=\"submit\" value=\"$submit_button\"$submit_disable>\n".
	"</td></tr>\n".
	"</table>\n".
	"<BR></form>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";
