#! C:\Perl\bin\perl.exe -I..\common

use strict;
use CGI;
use CGI::Carp qw(fatalsToBrowser);
use DirHandle;

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
my $str_STOP_HISTORY   		= &TMSstr::get_str( "STOP_HISTORY"		);
my $str_DELETING_DATA		= &TMSstr::get_str( "DELETING_DATA"		);
my $str_COMPLETED_ALL_PROPERLY	= &TMSstr::get_str( "COMPLETED_ALL_PROPERLY"	);

if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $html = new CGI;

my $month = $html->param('month');
my @shift = $html->param('shift');
my @loom  = $html->param('loom');

my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

if( $#shift < 0 ){ print &TMScommon::no_data_page( $menu_color, $body_color ); exit; }
if( $#loom  < 0 ){ print &TMScommon::no_data_page( $menu_color, $body_color ); exit; }

my $lockfile = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20,\$other_user) ){	# 同時使用を禁止（レベル１）
  print &TMSlock::data_updating_page( $other_user );
  exit;
}
my $lock_start = time();	# ロック開始時間

# ---------------------------------------------------------------------

# リダイレクトページの表示

my $title   = $str_DELETE_DATA.'('.$str_STOP_HISTORY.')';
my $cgifile = 'hist_delete.cgi';

print	"<html lang=$lang>\n".
	"<head>\n".
	&TMScommon::meta_content_type( $lang ).
	&TMScommon::meta_no_cache_tag().
	"<title>$title</title>\n".
	"<script language=JavaScript>\n".
	"<!--\n".
	"  function move_next_page() {\n".
	"    location.href = \"".$cgifile."?month=$month\";\n".
	"  }\n".
	"//-->\n".
	"</script>\n".
	"</head>\n".
	"<body bgcolor=$body_color OnLoad=\"setTimeout('move_next_page()',1000)\">\n".
	"<pre>\n";

# ---------------------------------------------------------------------

### 履歴フォルダの所在パスの設定 ###
my $stophist_dir = "..\\..\\tmsdata\\stop_history";

### 開始の表示 ###
print	"\n$str_DELETING_DATA\n\n";

### 経過表示 ###
my $total = ($#shift +1);
my $count = 0;
&TMScommon::disp_percent($total, $count);  # 経過表示（開始）

### 削除対象機台名 ###
my %loom = ();
foreach( @loom ){ $loom{$_} = 1; }

### 各選択期間に対して ###
foreach( @shift ){
  my $data_subdir = "$stophist_dir\\$_";

  ### 停止履歴データファイルの削除 #########################

  # データファイルの一覧を作成
  my $dir = new DirHandle $data_subdir;
  my @file_list = $dir->read;
  $dir->close;

  foreach my $file ( @file_list ){

    # "数字.txt" のファイルのみ対象
    if( ($file =~ m/^\d+\.txt$/) and
        (-f "$data_subdir\\$file") ){

      my $fullname = "$data_subdir\\$file";
      if( open(FILE, "< $fullname") ){
        my $line = <FILE>;  # １行目
        close(FILE);

        chomp $line; # 改行を除く
        my @data  = split(/,/, $line);
        my ($title, $mac_name) = split(/ /,$data[3], 2);

        if( defined($mac_name) ){
          if( exists($loom{$mac_name}) ){
            unlink( $fullname );
          }
        }
      }
    }
  }

  ### indexファイルの更新 ################################

  # 本来、再構築処理でindexファイルは作り直すが、
  # 編集画面の表示を更新する為ここでも更新する

  my $org_file = "$data_subdir\\index.txt";
  my $new_file = "$data_subdir\\index.new";

  if( open(ORG, "< $org_file") ){

    my $change_flg = 0;
    my $line_count = 0;
    if( open(NEW, "> $new_file") ){

      while( my $line = <ORG> ){
        chomp $line;
        my ($fix,$file,$mac_name) = split(/,/, $line);

        if( exists($loom{$mac_name}) ){ # 対象機台なら削除
          $change_flg = 1;
        }
        else{
          print NEW "$line\n";
          ++$line_count;
        }
      }
      close(NEW);
    }
    close(ORG);

    # 変更があった場合のみ、ファイルを置き換える
    if( $change_flg ){
      unlink( $org_file );
      if( $line_count > 0 ){  # 新規ファイルが１行以上
        rename( $new_file, $org_file );
      }else{
        unlink( $new_file );
      }
    }
    else{
      unlink( $new_file );
    }
  }


  ### 処理開始して１０秒経過したらロックファイルを更新（レベル１）###
  my $now = time();
  if( ($now - $lock_start) >= 10 ){ # 10秒
    $lock_start = $now;
    &TMSlock::update_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20);
  }

  &TMScommon::disp_percent($total, ++$count);  # 経過表示（途中）

}
&TMScommon::disp_percent(100,101);  # 経過表示（終了）

### データ再構築要求ファイルを作成 ###
&TMSrestruct::request_restruction();

### 機台名削除終了の表示 ###
print	"\n**** $str_COMPLETED_ALL_PROPERLY ****\n".
	"</pre>\n".
	"</body></html>\n";

unlink($lockfile);	# ロックファイルを削除

exit;

######################################################################
