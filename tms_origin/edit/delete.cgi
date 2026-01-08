#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);

use TMSstr;
use TMScommon;
use TMSdeny;
use TMSlock;
use TMSrestruct;

$| = 1;
require '../common/http_header.pm';

my $lang = &TMSstr::get_lang_set();
&TMSstr::load_str_file($lang);       # 必ず get_str() の前に実行する事！！

my $str_DELETE_DATA		= &TMSstr::get_str( "DELETE_DATA"		);
my $str_SHIFT_DATA		= &TMSstr::get_str( "SHIFT_DATA"		);
my $str_OPERATOR_DATA		= &TMSstr::get_str( "OPERATOR_DATA"		);
my $str_DELETING_DATA		= &TMSstr::get_str( "DELETING_DATA"		);
my $str_COMPLETED_ALL_PROPERLY	= &TMSstr::get_str( "COMPLETED_ALL_PROPERLY"	);

if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $html = new CGI;

my $sel_data = $html->param('data');
my $month    = $html->param('month');
my @shift    = $html->param('shift');
my @loom     = $html->param('loom');
my $all_loom = $html->param('all_loom');

my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

if( $#shift < 0 ){ print &TMScommon::no_data_page( $menu_color, $body_color ); exit; }
if( $#loom  < 0 ){ print &TMScommon::no_data_page( $menu_color, $body_color ); exit; }


my $lockfile = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20,\$other_user) ){  # 同時使用を禁止（レベル１）
  print &TMSlock::data_updating_page( $other_user );
  exit;
}
my $lock_start = time();	# ロック開始時間

# ---------------------------------------------------------------------

# リダイレクトページの表示

my $title = $str_DELETE_DATA;
if( $sel_data eq 'shift'    ){ $title .= " ($str_SHIFT_DATA)";    }
if( $sel_data eq 'operator' ){ $title .= " ($str_OPERATOR_DATA)"; }

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function move_next_page() {\n".
	"    location.href = \"select.cgi?mode=delete&data=$sel_data&month=$month\";\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('move_next_page()',1000)\">\n".
	"<pre>\n";

# ---------------------------------------------------------------------

my $data_dir;
if( $sel_data eq 'shift'    ){ $data_dir = "..\\..\\tmsdata\\shift";    }
if( $sel_data eq 'operator' ){ $data_dir = "..\\..\\tmsdata\\operator"; }

print	"\n$str_DELETING_DATA\n\n";

my $total = ($#shift +1);
my $count = 0;
&TMScommon::disp_percent($total, $count);  # 経過表示（開始）

foreach my $shiftnum ( @shift ){

  my $fname   = "$data_dir\\$shiftnum.txt";	# データファイル
  my $tmpname = "$data_dir\\$shiftnum.tmp";	# TMPファイル

  if( $all_loom eq "on" ){
    if( -f $fname ){ unlink($fname); }
  }
  elsif( open(IN,"< $fname") ){
    my $dcount = 0;
    if( open(OUT,"> $tmpname") ){
      my $del_count = 0;
      while(<IN>){
        my $line = $_;
        if( $line =~ m/,mac_name ([^,]*)/ ){
          my $lm = $1;
          my $match = 0;
          for( my $i=0; $i<=$#loom; $i++ ){
            if( $loom[$i] eq $lm ){ $match = 1; last; }
          }
          # 削除する機台に該当しなければ残す
          if( $match ){ ++$del_count; }
          else{ print OUT $line; ++$dcount; }
        }
      }
      close(OUT);

      # 更新無し、又は残ったデータ無ければ、消す。
      if( ($del_count == 0) || ($dcount == 0) ){ unlink($tmpname); }
    }
    close(IN);
    if( $dcount == 0 ){ unlink($fname); }	# 残ったデータ無ければ、元も消す。

    # TMPファイルをリネームする。
    if( -f $tmpname ){
      unlink($fname);
      rename( $tmpname, $fname );
    }
  }

  my $now = time();
  if( ($now - $lock_start) >= 10 ){	# 処理開始して１０秒経過したら。
    $lock_start = $now;
    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);		# ロックファイルを更新（レベル１）
  }

  &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中）
}

&TMScommon::disp_percent(100,101);  # 経過表示（終了）

# ----------------------------------------------------------------------------
# 機台名、品種のインデックスを削除する。

if( $sel_data eq 'shift'    ){
  unlink( "..\\..\\tmsdata\\index\\edit\\s_loom$month.txt" );
  unlink( "..\\..\\tmsdata\\index\\edit\\s_style$month.txt" );
}
elsif( $sel_data eq 'operator' ){
  unlink( "..\\..\\tmsdata\\index\\edit\\o_loom$month.txt" );
  unlink( "..\\..\\tmsdata\\index\\edit\\o_style$month.txt" );
}

# ----------------------------------------------------------------------------
# データ再構築要求ファイルを作成

&TMSrestruct::request_restruction();

# ----------------------------------------------------------------------------

print	"\n**** $str_COMPLETED_ALL_PROPERLY ****\n".
	"</pre>\n".
	"</body></html>\n";

unlink($lockfile);	# ロックファイルを削除

exit;

