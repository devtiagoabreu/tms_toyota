#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSscanner;

require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SETTING_RESULT	= &TMSstr::get_str( "SETTING_RESULT"	);
my $str_SETTING_SUCCEED	= &TMSstr::get_str( "SETTING_SUCCEED"	);
my $str_MENU		= &TMSstr::get_str( "MENU"		);
my $str_BACK		= &TMSstr::get_str( "BACK"		);

#######################################################

my $html = new CGI;

my $mac_id          = $html->param('mac_id');
my $style           = $html->param('style');
my $use_doff_length = $html->param('use_doff_length');
my $doff_length     = $html->param('doff_length');
my $beam            = $html->param('beam');
my $beam_set        = $html->param('beam_set');
my $beam_shrinkage  = $html->param('beam_shrinkage');
my $ubeam           = $html->param('ubeam');
my $ubeam_set       = $html->param('ubeam_set');
my $ubeam_shrinkage = $html->param('ubeam_shrinkage');

my $correct_cloth = $html->param('correct_cloth');
my $cloth_length  = $html->param('cloth_length');

my $correct_beam  = $html->param('correct_beam');
my $beam_remain   = $html->param('beam_remain');

my $correct_ubeam = $html->param('correct_ubeam');
my $ubeam_remain  = $html->param('ubeam_remain');


### 設定値の更新 ###

$doff_length = int($doff_length);

$beam =~ s/^\s+//g;  # 先頭のスペースを除去
$beam =~ s/\s+$//g;  # 末尾のスペースを除去
$beam_set       = int($beam_set);
$beam_shrinkage = sprintf("%.1f",$beam_shrinkage);

$ubeam =~ s/^\s+//g;  # 先頭のスペースを除去
$ubeam =~ s/\s+$//g;  # 末尾のスペースを除去
$ubeam_set       = int($ubeam_set);
$ubeam_shrinkage = sprintf("%.1f",$ubeam_shrinkage);

my @loom_set = ();
@{$loom_set[0]} = ( $mac_id,
                    $style,
                    $use_doff_length,
                    $doff_length,
                    $beam,
                    $beam_set,
                    $beam_shrinkage,
                    $ubeam,
                    $ubeam_set,
                    $ubeam_shrinkage );

&TMSscanner::update_loom_setting( \@loom_set,
                                  "style",
                                  "use_doff_length",
                                  "doff_length",
                                  "beam",
                                  "beam_set",
                                  "beam_shrinkage",
                                  "ubeam",
                                  "ubeam_set",
                                  "ubeam_shrinkage" );



#### クロス長、残りビーム長の変更 ####

my @scan_ip = &TMSscanner::get_scan_ip();

if( $mac_id =~ m/S([1-5])-([0-9]+)\.([0-9]+)/ ){
  my $scan_no = $1;  # 対象のスキャナーだけ
  my $mainte_fname = sprintf("mainte/%02d%03d.txt",$2,$3);

  my @mainte = ();
  if( $correct_cloth ){
    $cloth_length = sprintf("%.1f",$cloth_length);
    push(@mainte,"cloth_length $cloth_length");
  }
  if( $correct_beam ){
    $beam_remain = sprintf("%.1f",$beam_remain);
    push(@mainte,"beam_remain $beam_remain");
  }
  if( $correct_ubeam ){
    $ubeam_remain = sprintf("%.1f",$ubeam_remain);
    push(@mainte,"ubeam_remain $ubeam_remain");
  }

  if( $#mainte >= 0 ){
    &TMSscanner::upload_scanner_file($scan_no,$mainte_fname,\@mainte);
  }
}

## 画面表示 ########################################

my $tbl_width = 630;
my $title = $str_SETTING_RESULT;
my $menu_color = '#fdb913';
my $body_color = '#fff2dd';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"</head>\n".
	"<body bgcolor=#C7C4E2><center>\n".
	&TMScommon::make_header('menu','dummy', $lang)."<BR>".

	"<table border=1 frame=box width=$tbl_width cellPadding=6>\n".
	"<tr align=center bgcolor=$menu_color>\n".
	"<th><font size=+2 color=white>$title</font></th>\n".
	"</tr>\n".
	"<tr align=center bgcolor=$body_color><td>\n".
	"<BR><BR><BR>\n";

  print	"<font size=+2><B>$str_SETTING_SUCCEED</B></font>\n";

print	"<BR><BR><BR>\n".
	"<NOBR>\n".
	"<A HREF=\"../\"><IMG SRC=\"../image/menu2_$lang.jpg\" width=85 height=27 alt=\"$str_MENU\" border=0></A>\n".
	"<A HREF=\"clothbeammainte.cgi\"><IMG SRC=\"../image/back2_$lang.jpg\" width=85 height=27 alt=\"$str_BACK\" border=0></A>\n".
	"</NOBR>\n".
	"<BR><BR><BR><BR>\n".
	"</td></tr>\n".
	"</table><BR>\n".

	&TMScommon::make_footer('dummy','menu', $lang).
	"</center></body></html>\n";

