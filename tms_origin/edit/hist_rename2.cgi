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

my $str_CHANGE_LOOM_NAME	= &TMSstr::get_str( "CHANGE_LOOM_NAME"		);
my $str_STOP_HISTORY   		= &TMSstr::get_str( "STOP_HISTORY"		);
my $str_CHANGEING_DATA		= &TMSstr::get_str( "CHANGEING_DATA"		);
my $str_COMPLETED_ALL_PROPERLY	= &TMSstr::get_str( "COMPLETED_ALL_PROPERLY"	);

if( $ENV{REMOTE_ADDR} ne '127.0.0.1' ){
  print &TMSdeny::permission_deny_page();
  exit;
}

my $html = new CGI;

my $month    = $html->param('month');
my @shift    = $html->param('shift');
my $loom_org = $html->param('loom');
my $loom_new = $html->param('new_loom');
if( length($loom_new) > 0 ){
  $loom_new =~ s/,/_/g;		# , はアンダーバーへ
  $loom_new =~ s/"/_/g;		# " はアンダーバーに変換。
  $loom_new =~ s/\s+/ /g;	# ２個以上のスペースを１個にする。
  $loom_new =~ s/^\s//;		# 先頭のスペースを削除。
  $loom_new =~ s/\s$//;		# 最後のスペースを削除。
}

my $menu_color = '#0080EF';
my $body_color = '#D5E8F8';

if( ($#shift < 0) || (length($loom_org) == 0) || (length($loom_new) == 0) ){
  print &TMScommon::no_data_page( $menu_color, $body_color );
  exit;
}


my $lockfile = '../../tmsdata/update.lock';
my $other_user;
if( &TMSlock::create_lockfile($lockfile,$ENV{REMOTE_ADDR},1,20,\$other_user) ){	# 同時使用を禁止（レベル１）
  print &TMSlock::data_updating_page( $other_user );
  exit;
}
my $lock_start = time();	# ロック開始時間

# ---------------------------------------------------------------------

# リダイレクトページの表示

my $title   = $str_CHANGE_LOOM_NAME.'('.$str_STOP_HISTORY.')';
my $cgifile = 'hist_rename.cgi';

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

### 機台名変更開始の表示 ###
print	"\n$str_CHANGEING_DATA\n\n";

### 経過表示 ###
my $total = ($#shift +1);
my $count = 0;
&TMScommon::disp_percent($total, $count);  # 経過表示（開始）

### 各選択期間に対して ###
foreach( @shift ){
  my $data_subdir = "$stophist_dir\\$_";

  ### 停止履歴データファイルの更新 #########################

  # データファイルの一覧を作成
  my $dir = new DirHandle $data_subdir;
  my @file_list = $dir->read;
  $dir->close;

  foreach my $file ( @file_list ){

    # "数字.txt" のファイルのみ対象
    if( ($file =~ m/^\d+\.txt$/ ) and
        (-f "$data_subdir\\$file") ){

      my $org_file = "$data_subdir\\$file";

      # 更新用ファイル名
      my $new_file = $org_file;
      $new_file =~ s/txt$/new/;  # 拡張子を txt -> new へ

      if( open(ORG, "< $org_file") ){
        my $change_flg = 0;

        my $line = <ORG>;  # １行目
        chomp $line; # 改行を除く

        my @data  = split(/,/, $line);
        if( $data[3] eq "mac_name $loom_org" ){
          $data[3] = "mac_name $loom_new";  # 機台名を変更

          ### 更新用ファイルに書き出し ###############
          if( open(NEW, "> $new_file") ){

            $line = "";
            foreach(@data){ $line .= $_.","; }  # 項目数がLWT対応で増えているので注意
            chop $line;  # 最後の , を消す
            print NEW $line."\n";         # １行目

            while( <ORG> ){ print NEW; }  # ２行目以降

            close(NEW);
            $change_flg = 1;
          }
        }
        close(ORG);

        # 変更があった場合のみ、ファイルを置き換える
        if( $change_flg ){
          unlink( $org_file );
          rename( $new_file, $org_file );
        }
        else{
          unlink( $new_file );
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

    if( open(NEW, "> $new_file") ){

      while( my $line = <ORG> ){
        chomp $line;
        my ($fix,$file,$mac_name) = split(/,/, $line);

        if( $mac_name eq $loom_org ){ # 対象機台なら変更
          print NEW "$fix,$file,$loom_new\n";
          $change_flg = 1;
        }
        else{ # 対象機台でなければ変更しない
          print NEW "$line\n";
        }
      }
      close(NEW);
    }
    close(ORG);

    # 変更があった場合のみ、ファイルを置き換える
    if( $change_flg ){
      unlink( $org_file );
      rename( $new_file, $org_file );
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

### 機台名変更終了の表示 ###
print	"\n**** $str_COMPLETED_ALL_PROPERLY ****\n".
	"</pre>\n".
	"</body></html>\n";

unlink($lockfile);	# ロックファイルを削除

exit;

######################################################################
