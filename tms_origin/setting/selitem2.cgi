#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSlock;
use TMSrestruct;
use TMSselitem;
use TMSDATAfinal;
use TMSDATAindex;

$| = 1;
require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_SETTING_RESULT		= &TMSstr::get_str( "SETTING_RESULT"		);
my $str_APPLY_CHANGE_TO_DATA	= &TMSstr::get_str( "APPLY_CHANGE_TO_DATA"	);
my $str_COMPLETED_ALL_PROPERLY	= &TMSstr::get_str( "COMPLETED_ALL_PROPERLY"	);

my $old_val_week   = &TMSselitem::get_value_of_week();
my $old_val_effic  = &TMSselitem::get_value_of_effic();
my $old_val_run_tm = &TMSselitem::get_value_of_run_tm();

my $html = new CGI;

my @prm_item2  = $html->param('item2');
my @prm_item   = $html->param('item');
my @prm_item3  = $html->param('item3');
my @prm_detail = $html->param('detail');
my @prm_color  = $html->param('color');
my $prm_bmtype = $html->param('beam_type');
my $prm_unit   = $html->param('unit');
my $prm_period = $html->param('period');
my $prm_week   = $html->param('week');
my $prm_effic  = $html->param('effic');
my $prm_run_tm = $html->param('run_tm');
my $prm_expire = $html->param('expire');

my @key_item2  = &TMSselitem::get_key_of_item2();
my @key_item   = &TMSselitem::get_key_of_item();
my @key_item3  = &TMSselitem::get_key_of_item3();
my @key_detail = &TMSselitem::get_key_of_detail();
my @key_color  = &TMSselitem::get_key_of_color();
my @key_bmtype = &TMSselitem::get_key_of_beam_type();
my @key_unit   = &TMSselitem::get_key_of_unit();
my @key_period = &TMSselitem::get_key_of_period();
my @key_week   = &TMSselitem::get_key_of_week();

my @val_item2 = ();
for(my $i=0; $i<=$#key_item2; $i++ ){
  $val_item2[$i] = 0;
  my $key = $key_item2[$i];
  foreach(@prm_item2){
    if( $_ eq $key ){ $val_item2[$i] = 1; last; }
  }
}

my @val_item = ();
for(my $i=0; $i<=$#key_item; $i++ ){
  $val_item[$i] = 0;
  my $key = $key_item[$i];
  foreach(@prm_item){
    if( $_ eq $key ){ $val_item[$i] = 1; last; }
  }
}

my @val_item3 = ();
for(my $i=0; $i<=$#key_item3; $i++ ){
  $val_item3[$i] = 0;
  my $key = $key_item3[$i];
  foreach(@prm_item3){
    if( $_ eq $key ){ $val_item3[$i] = 1; last; }
  }
}

my @val_detail = ();
for(my $i=0; $i<=$#key_detail; $i++ ){
  $val_detail[$i] = 0;
  my $key = $key_detail[$i];
  foreach(@prm_detail){
    if( $_ eq $key ){ $val_detail[$i] = 1; last; }
  }
}

my @val_color = ();
for(my $i=0; $i<=$#key_color; $i++ ){
  $val_color[$i] = 0;
  my $key = $key_color[$i];
  foreach(@prm_color){
    if( $_ eq $key ){ $val_color[$i] = 1; last; }
  }
}

my $val_bmtype = &TMSselitem::get_value_of_beam_type();
foreach(@key_bmtype){
  if( $_ eq $prm_bmtype){ $val_bmtype = $prm_bmtype; last; }
}

my $val_unit = &TMSselitem::get_value_of_unit();
foreach(@key_unit){
  if( $_ eq $prm_unit){ $val_unit = $prm_unit; last; }
}

my $val_period = &TMSselitem::get_value_of_period();
foreach(@key_period){
  if( $_ eq $prm_period){ $val_period = $prm_period; last; }
}

my $val_week = &TMSselitem::get_value_of_week();
foreach(@key_week){
  if( $_ eq $prm_week){ $val_week = $prm_week; last; }
}

my $val_effic = 0;
if( $prm_effic ne "" ){ $val_effic = $prm_effic; }

my $val_run_tm = 0;
if( $prm_run_tm ne "" ){ $val_run_tm = $prm_run_tm; }

my $val_expire = 1;
if( $prm_expire ne "" ){
  if( $prm_expire >= 1 ){  # １時間未満は設定不可
    $val_expire = $prm_expire;
  }
}


# モニターデータを、再構築するかどうかチェック
my $update_level = 0;
if(    $old_val_effic  ne $val_effic  ){ $update_level = 1; }	# 全データを更新
elsif( $old_val_run_tm ne $val_run_tm ){ $update_level = 1; }	# 全データを更新
elsif( $old_val_week   ne $val_week   ){ $update_level = 2; }	# 週データのみ変更


if( $update_level == 0 ){	# データ更新の必要無い場合 -------------------------------------------

  # 設定ファイルに設定値保存
  &TMSselitem::save_selitem_val(
	\@val_item2,
	\@val_item,
	\@val_item3,
	\@val_detail,
	\@val_color,
	$val_bmtype,
	$val_unit,
	$val_period,
	$val_week,
	$val_effic,
	$val_run_tm,
	$val_expire	);

  print	"<HTML><HEAD><META HTTP-EQUIV=\"Refresh\" CONTENT=\"0; URL=selitem3.cgi\"></HEAD>\n".
	"<BODY bgcolor=#C7C4E2></BODY></HTML>";

  exit;

}
else{ 	# データ更新が必要な場合 --------------------------------------------------------------------

  # データ更新中は、稼働率、運転時間、週の設定値変更を受け付けない
  my $lockfile = '../../tmsdata/update.lock';
  my $other_user;
  if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20,\$other_user) ){	# 同時使用を禁止（レベル１）
    print &TMSlock::data_updating_page( $other_user );
    exit;
  }

  # 設定ファイルに設定値保存
  &TMSselitem::save_selitem_val(
	\@val_item2,
	\@val_item,
	\@val_item3,
	\@val_detail,
	\@val_color,
	$val_bmtype,
	$val_unit,
	$val_period,
	$val_week,
	$val_effic,
	$val_run_tm,
	$val_expire	);


  # リダイレクトページの表示

  #my $menu_color = '#ED1C24';
  my $body_color = '#FDE1D4';

  my $title = $str_SETTING_RESULT;

  print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function move_next_page() {\n".
	"    location.href = \"selitem3.cgi\";\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('move_next_page()',2000)\">\n".
	"<pre>\n";

  #------------------------------------------------------------------------------
  # 稼働率、運転時間、週の設定が変更されたら、データを作り直す

  print	"\n$str_APPLY_CHANGE_TO_DATA\n\n";

  if( $update_level == 1 ){	# 全データを更新

    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);  # ロックファイルを更新（レベル１）

    &TMSDATAfinal::update_all_request();
    &TMSDATAfinal::make_final( 1 );  # Phase 1

    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);  # ロックファイルを更新（レベル１）

    &TMSDATAindex::make_index( 2 );  # Phase 2

    &TMSrestruct::clr_restruction_request();  # データ再構築要求ファイルを削除
  }
  elsif( $update_level == 2 ){	# 週データのみ変更

    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);  # ロックファイルを更新（レベル１）

    &TMSDATAfinal::update_week_request();
    &TMSDATAfinal::make_week_final( 1 );  # Phase 1

    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,600);  # ロックファイルを更新（レベル１）

    &TMSDATAindex::make_week_index( 2 );  # Phase 2
  }

  #------------------------------------------------------------------------------

  print "\n**** $str_COMPLETED_ALL_PROPERLY ****\n".
	"</pre>\n".
	"</body></html>\n";

  unlink($lockfile);	# ロックファイルを削除

}

