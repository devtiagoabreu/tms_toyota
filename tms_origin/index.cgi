#! C:\Perl\bin\perl.exe -Icommon

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;

my $version = "Version 7.0";  # 7.03

require 'common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_MAIN_MENU			= &TMSstr::get_str( "MAIN_MENU"			);
my $str_SHIFT_DATA			= &TMSstr::get_str( "SHIFT_DATA"		);
my $str_OPERATOR_DATA			= &TMSstr::get_str( "OPERATOR_DATA"		);
my $str_LOOM_DATA			= &TMSstr::get_str( "LOOM_DATA"			);
my $str_SETTING				= &TMSstr::get_str( "SETTING"			);
my $str_SHIFT_REPORT			= &TMSstr::get_str( "SHIFT_REPORT"		);
my $str_STYLE_REPORT			= &TMSstr::get_str( "STYLE_REPORT"		);
my $str_STATUS_HISTORY			= &TMSstr::get_str( "STATUS_HISTORY"		);
my $str_OPERATOR_REPORT			= &TMSstr::get_str( "OPERATOR_REPORT"		);
my $str_PRODUCTION_GRAPH		= &TMSstr::get_str( "PRODUCTION_GRAPH"		);
my $str_EFFICIENCY_GRAPH		= &TMSstr::get_str( "EFFICIENCY_GRAPH"		);
my $str_STOP_ANALYSIS_GRAPH		= &TMSstr::get_str( "STOP_ANALYSIS_GRAPH"	);
my $str_YARN_INVENTORY_FORECAST		= &TMSstr::get_str( "YARN_INVENTORY_FORECAST"	);
my $str_STOP_HISTORY			= &TMSstr::get_str( "STOP_HISTORY"		);
my $str_DATA_COLLECTION_NETWORK		= &TMSstr::get_str( "DATA_COLLECTION_NETWORK"	);
my $str_DATA_IMPORT_MEMCARD		= &TMSstr::get_str( "DATA_IMPORT_MEMCARD"	);
my $str_LINK_TO_LOOM_SCREEN		= &TMSstr::get_str( "LINK_TO_LOOM_SCREEN"	);
my $str_LOOM_CLOCK_SETTING		= &TMSstr::get_str( "LOOM_CLOCK_SETTING"	);
my $str_EXPORT_CSV_FILE			= &TMSstr::get_str( "EXPORT_CSV_FILE"		);
my $str_REPORT_SETTING			= &TMSstr::get_str( "REPORT_SETTING"		);
my $str_OTHER_SETTING			= &TMSstr::get_str( "OTHER_SETTING"		);
my $str_PASSWORD_SETTING		= &TMSstr::get_str( "PASSWORD_SETTING"		);
my $str_DOWNLOAD_TMS_HELPER		= &TMSstr::get_str( "DOWNLOAD_TMS_HELPER"	);
my $str_DATA_EDIT			= &TMSstr::get_str( "DATA_EDIT"			);
my $str_DATA_EDIT_MENU			= &TMSstr::get_str( "DATA_EDIT_MENU"		);

my $str_OPERATION_STATUS 		= &TMSstr::get_str( 'OPERATION_STATUS' 		);
my $str_CLOTH_BEAM_LIST_SETTING		= &TMSstr::get_str( 'CLOTH_BEAM_LIST_SETTING'	);
my $str_OTHER_LIST_SETTING		= &TMSstr::get_str( 'OTHER_LIST_SETTING'	);
my $str_CLOTH_BEAM_MAINTENANCE		= &TMSstr::get_str( 'CLOTH_BEAM_MAINTENANCE'	);
my $str_SCANNER_SETTING			= &TMSstr::get_str( 'SCANNER_SETTING'		);
my $str_STYLE_SETTING			= &TMSstr::get_str( 'STYLE_SETTING'		);
my $str_SHIFT_SCHEDULE_SETTING		= &TMSstr::get_str( 'SHIFT_SCHEDULE_SETTING'	);
my $str_UNIT_SETTING			= &TMSstr::get_str( 'UNIT_SETTING'		);
my $str_LOOM_NAME_SPEC_SETTING		= &TMSstr::get_str( 'LOOM_NAME_SPEC_SETTING'	);

my $str_SERVICE_REPORT			= &TMSstr::get_str( "SERVICE_REPORT"		);
my $str_LANGUAGE_SETTING		= &TMSstr::get_str( "LANGUAGE_SETTING"		);
my $str_SWITCH_USE_DATA			= &TMSstr::get_str( "SWITCH_USE_DATA"		);

my $JAT710_ARI  = ( -f "..\\tmsdata\\setting\\ipaddress.txt"  );
my $MEMCARD_ARI = ( -f "..\\tmsdata\\setting\\memcard.txt"    );
my $SCANNER_ARI = ( -f "..\\tmsdata\\setting\\scanner_ip.txt" );

# サービス員用機能ありか？
my $SERVICE_MODE = (1==0); # False
my $service_txt = "setting\\service.txt";
if( -f $service_txt ){
  if( open(FILE,"< $service_txt") ){
    my $data = <FILE>;
    close(FILE);
    chomp $data;
    if( $data eq "1" ){ $SERVICE_MODE = (1==1); } # True
  }
  if( ! $SERVICE_MODE ){ unlink($service_txt); }
}

my $url_tmsscaner_passwd_scanloom = "";
my $url_tmsscaner_passwd_scanset = "";
if( $SCANNER_ARI ){
  if( open(IPADDR,'< ../tmsdata/setting/scanner_ip.txt') ){
    my $scan1_ip = <IPADDR>;
    close(IPADDR);

    $scan1_ip =~ s/\n$//;	# 改行コードを削除。
    $scan1_ip =~ s/\s//g;	# スペースを削除。

    $url_tmsscaner_passwd_scanloom = "http://$scan1_ip/TmsScanner/passwd/scanloom/redir.cgi";
    $url_tmsscaner_passwd_scanset  = "http://$scan1_ip/TmsScanner/passwd/scanset/redir.cgi";
  }
}

my $tbl_width = 285;
my $box_space = 5;
my $top_space = 5;
my $cell_spacing = 2;
my $cell_padding = 0;

print	"<HTML lang=$lang>\n".
	"<HEAD>\n".
	"<STYLE TYPE=\"text/css\">\n".
	"A:link    { color: Midnightblue }\n".
	"A:visited { color: Midnightblue }\n".
	"A:active  { color: Red }\n".
	"</STYLE>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<TITLE>$str_MAIN_MENU</TITLE></HEAD>\n".
	"<BODY bgcolor=#C7C4E2>\n".
	"<CENTER>\n".
	&TMScommon::make_header('dummy','dummy', $lang ).

# 全体のテーブル
	"<TABLE border=0 cellSpacing=0 cellPadding=0>\n".
	"<TR><TD colspan=3 align=center><IMG src=\"image/TMS.jpg\" width=640 height=50 alt=\"TOYOTA Monitoring System\"></TD></TR>\n".
	"<TR><TD colspan=3 align=right><B>$version&nbsp;&nbsp;&nbsp;&nbsp;</B></TD></TR>\n".
	"<TR valign=top><TD>\n".

# 左側の列 -------------------------------------------------
	"<TABLE border=0>\n".

	"<TR><TD align=center><IMG SRC=\"image/tab_shift_$lang.jpg\" width=310 height=40 alt=\"$str_SHIFT_DATA\"></TD></TR>\n".
	"<TR><TD bgcolor=#E1E2F2>\n".
	"<table width=$tbl_width align=right cellSpacing=$cell_spacing cellPadding=$cell_padding>\n".
	"<tr><td height=$top_space></td></tr>\n";

if( $SERVICE_MODE ){ # サービス員用
  print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift2/select_s2.cgi?mode=svsreport&period=shift\"><B>$str_SERVICE_REPORT</B></A></td></tr>\n".
	"<tr><td><hr width=90% align=left></td></tr>\n";
}
print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/select_s.cgi?mode=shiftreport\"><B>$str_SHIFT_REPORT</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/select_s.cgi?mode=stylereport\"><B>$str_STYLE_REPORT</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/select_s.cgi?mode=statushistory\"><B>$str_STATUS_HISTORY</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/select_s.cgi?mode=production\"><B>$str_PRODUCTION_GRAPH</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/select_s.cgi?mode=efficiency\"><B>$str_EFFICIENCY_GRAPH</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/select_s.cgi?mode=stopanalysis\"><B>$str_STOP_ANALYSIS_GRAPH</B></A></td></tr>\n".
	"<tr><td><hr width=90% align=left></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/select_s.cgi?mode=forecast\"><B>$str_YARN_INVENTORY_FORECAST</B></A></td></tr>\n";
if( $JAT710_ARI or $MEMCARD_ARI ){
  print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"shift/stophistory.cgi\"><B>$str_STOP_HISTORY</B></A></td></tr>\n";
}


print	"</table>\n".
	"</TD></TR>\n".

	"<TR><TD height=$box_space></TD></TR>\n".

	"<TR><TD align=center><IMG SRC=\"image/tab_loom_$lang.jpg\" width=310 height=40 alt=\"$str_LOOM_DATA\"></TD></TR>\n".
	"<TR><TD bgcolor=#FFF2DD>\n".
	"<table width=$tbl_width align=right cellSpacing=$cell_spacing cellPadding=$cell_padding>\n".
	"<tr><td height=$top_space></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"loom/opestate.cgi\"><B>$str_OPERATION_STATUS</B></A></td></tr>\n".
	"<tr><td><hr width=90% align=left></td></tr>\n";

if( $JAT710_ARI or $SCANNER_ARI ){
  print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"loom/getdata.cgi\"><B>$str_DATA_COLLECTION_NETWORK</B></A></td></tr>\n";
}
if( $MEMCARD_ARI or $SERVICE_MODE ){ # サービス員用も
  print "<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"loom/mcdata.cgi\"><B>$str_DATA_IMPORT_MEMCARD</B></A></td></tr>\n";
}
if( $JAT710_ARI ){
  print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"loom/linkmenu.cgi\"><B>$str_LINK_TO_LOOM_SCREEN</B></A></td></tr>\n";
}
if( $JAT710_ARI or $SCANNER_ARI ){
  print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"loom/setclock.cgi\"><B>$str_LOOM_CLOCK_SETTING</B></A></td></tr>\n";
}
if( $SCANNER_ARI ){
  print "<tr><td><hr width=90% align=left></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanloom?url=scanloom/clothbeamset.cgi\"><B>$str_CLOTH_BEAM_LIST_SETTING</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanloom?url=scanloom/otherset.cgi\"><B>$str_OTHER_LIST_SETTING</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanloom?url=scanloom/clothbeammainte.cgi\"><B>$str_CLOTH_BEAM_MAINTENANCE</B></A></td></tr>\n";
}
print	"</table>\n".
	"</TD></TR>\n".
	"</TABLE></TD>\n";

# 真ん中の隙間 ------------------------------------------
if( $lang eq 'zh-cn' )
    { print	"<TD>&nbsp;</TD>\n"; }
else{ print	"<TD>&nbsp;&nbsp;</TD>\n"; }

# 右側の列 ----------------------------------------------
print	"<TD><TABLE border=0>\n";

if( $JAT710_ARI or $MEMCARD_ARI ){
  print	"<TR><TD align=center><IMG SRC=\"image/tab_operator_$lang.jpg\" width=310 height=40 alt=\"$str_OPERATOR_DATA\"></TD></TR>\n".
	"<TR><TD bgcolor=#DCEFE7>\n".
	"<table width=$tbl_width align=right cellSpacing=$cell_spacing cellPadding=$cell_padding>\n".
	"<tr><td height=$top_space></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"operator/select_p.cgi?mode=shiftreport\"><B>$str_OPERATOR_REPORT</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"operator/select_p.cgi?mode=production\"><B>$str_PRODUCTION_GRAPH</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"operator/select_p.cgi?mode=efficiency\"><B>$str_EFFICIENCY_GRAPH</B></A></td></tr>\n".
	"</table>\n".
	"</TD></TR>\n".

	"<TR><TD height=$box_space></TD></TR>\n";
}

print	"<TR><TD align=center><IMG SRC=\"image/tab_setting_$lang.jpg\" width=310 height=40 alt=\"$str_SETTING\"></TD></TR>\n".
	"<TR><TD bgcolor=#FDE1D4>\n".
	"<table width=$tbl_width align=right cellSpacing=$cell_spacing cellPadding=$cell_padding>\n".
	"<tr><td height=$top_space></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"setting/selitem.cgi\"><B>$str_REPORT_SETTING</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"setting/otherset.cgi\"><B>$str_OTHER_SETTING</B></A></td></tr>\n";

if( $SERVICE_MODE ){ # サービス員用
  print "<tr><td><hr width=90% align=left></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"setting/langset.cgi\"><B>$str_LANGUAGE_SETTING</B></A></td></tr>\n";
}
if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){  # リモートの場合のみ
  print "<tr><td><hr width=90% align=left></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"TmsHelper-1.10.msi\"><B>$str_DOWNLOAD_TMS_HELPER</B></A></td></tr>\n";
}
print	"</table>\n".
	"</TD></TR>\n";

if( $SCANNER_ARI ){
  print	"<TR><TD height=$box_space></TD></TR>\n".

	"<TR><TD align=center><IMG SRC=\"image/tab_scanset_$lang.jpg\" width=310 height=40 alt=\"$str_SCANNER_SETTING\"></TD></TR>\n".
	"<TR><TD bgcolor=#FDE1D4>\n".
	"<table width=$tbl_width align=right cellSpacing=$cell_spacing cellPadding=$cell_padding>\n".
	"<tr><td height=$top_space></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanset?url=scanset/styleset.cgi\"><B>$str_STYLE_SETTING</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanset?url=scanset/shiftset.cgi\"><B>$str_SHIFT_SCHEDULE_SETTING</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanset?url=scanset/unitset.cgi\"><B>$str_UNIT_SETTING</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanset?url=scanset/loomspecset.cgi\"><B>$str_LOOM_NAME_SPEC_SETTING</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"$url_tmsscaner_passwd_scanset?url=scanset/passwd.cgi\"><B>$str_PASSWORD_SETTING</B></A></td></tr>\n".
	"</table>\n".
	"</TD></TR>\n";
}

print	"<TR><TD height=$box_space></TD></TR>\n".

	"<TR><TD align=center><IMG SRC=\"image/tab_edit_$lang.jpg\" width=310 height=40 alt=\"$str_DATA_EDIT\"></TD></TR>\n".
	"<TR><TD bgcolor=#D5E8F8>\n".
	"<table width=$tbl_width align=right cellSpacing=$cell_spacing cellPadding=$cell_padding>\n".
	"<tr><td height=$top_space></td></tr>\n";

if( $SERVICE_MODE ){ # サービス員用
  print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"edit2/switchdata.cgi\"><B>$str_SWITCH_USE_DATA</B></A></td></tr>\n".
	"<tr><td><hr width=90% align=left></td></tr>\n";
}
print	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"edit/\"><B>$str_DATA_EDIT_MENU</B></A></td></tr>\n".
	"<tr><td nowrap><img src=\"image/m.gif\" width=20 height=20 align=middle><A href=\"edit/exportcsv.cgi\"><B>$str_EXPORT_CSV_FILE</B></A></td></tr>\n".
	"</table>\n".
	"</TD></TR>\n".

	"</TABLE>\n".

	"</TD></TR>\n".
	"<TR><TD colspan=3>&nbsp;<BR></TD></TR>\n".
	"</TABLE>\n".
	&TMScommon::make_footer('dummy','dummy', $lang ).
	"</CENTER></BODY></HTML>";


###################################################################################################
#### lotate Apache logs ####

my $access_log = '../../logs/access.log';
my $error_log  = '../../logs/error.log';

if( -f $access_log ){

  my @filestat = stat $access_log;
  my $logsize = $filestat[7];
  if( $logsize >= (200*1024) ){  # 200KB

    if( -f "$access_log.3" ){ unlink( "$access_log.3" ); }
    if( -f "$error_log.3"  ){ unlink( "$error_log.3"  ); }

    if( -f "$access_log.2" ){ rename( "$access_log.2", "$access_log.3" ); }
    if( -f "$error_log.2"  ){ rename( "$error_log.2",  "$error_log.3"  ); }

    if( -f "$access_log.1" ){ rename( "$access_log.1", "$access_log.2" ); }
    if( -f "$error_log.1"  ){ rename( "$error_log.1",  "$error_log.2"  ); }

    rename( $access_log, "$access_log.1" );
    rename( $error_log,  "$error_log.1"  );
  }
}

###################################################################################################
