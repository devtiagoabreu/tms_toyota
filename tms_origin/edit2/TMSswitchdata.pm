package TMSswitchdata;

###################################################################################################
#
# TMSswitchdata.pm
#
###################################################################################################

use strict;

#----------------------------------------------------------------------------------------------------
# 保存データ名のリスト作成

sub get_save_data_name
{
  my ($r_list) = @_;

  my $rootdir = "..\\..";
  if( opendir(DIR,$rootdir) ){	# ディレクトリ、ファイルのリストを取得
    my @all_dir = readdir(DIR);
    closedir(DIR);

    foreach my $dir_name ( @all_dir){
      if( $dir_name =~ m/^tmsdata\.(.+)/ ){	# 保存されているデータの場合
        my $data_name = $1;
        if( -d "$rootdir\\$dir_name" ){
          push(@$r_list,$data_name);

          my $save_fname = "$rootdir\\$dir_name\\savename.txt";
          my $savename = "";
          if( -f $save_fname ){			# データ名が付いている場合
            if( open( FILE,"< $save_fname" ) ){
              $savename = <FILE>;
              close(FILE);
            }
          }
          if( $savename ne $data_name ){	# ディレクトリ名とデータ名不一致なら更新
            if( open( FILE,"> $save_fname" ) ){
              print FILE $data_name;
              close(FILE);
            }
          }
        }
      }
    }
  }
}

#----------------------------------------------------------------------------------------------------
# 現在データ名の取得

sub get_current_data_name
{
  my ($r_list) = @_;

  my $data_name = "";
  my $old_name = "";

  my $rootdir = "..\\..";
  if( -d "$rootdir\\tmsdata" ){				# 現在使用中のデータを調べる
    my $save_fname = "$rootdir\\tmsdata\\savename.txt";
    if( -f $save_fname ){				# データ名が付いている場合
      if( open( FILE,"< $save_fname" ) ){
        $data_name = <FILE>;
        close(FILE);
        $old_name = $data_name;
        $data_name =~ s/\s//g;		# スペースを削除する。
      }
    }

    if( length($data_name) > 0 ){ $data_name = &name_check($r_list,$data_name);   } # データ名が付いている場合
    else{                         $data_name = &name_check($r_list,"NoName_001"); } # データ名が無い場合

    if( $old_name ne $data_name ){		# 名前が変わったら
      if( open( FILE,"> $save_fname" ) ){
        print FILE "$data_name";		# 名前を保存
        close(FILE);
      }
    }
    push(@$r_list, $data_name);
  }
  return $data_name;
}

#----------------------------------------------------------------------------------------------------
# データ名の重複を避ける

sub name_check
{
  my ($r_list,$name) = @_;

  # 文字列を大文字に変換(ディレクトリ名は、大文字小文字の区別無い為）
  my $uc_name = uc($name);
  my @uc_list = ();
  foreach(@$r_list){ my $d = uc($_); push(@uc_list,$d); }

  # 比較
  my $dup = 0;
  foreach(@uc_list){ if( $uc_name eq $_ ){ $dup = 1; last; } }

  if( $dup ){	# 一致していた場合
    my $head = $name;
    if( $name =~ m/^(.+)_([0-9]+)$/ ){ $head = $1; }		# 末尾の数字を削除
    my $uc_head = uc($head);

    my $max = 0;
    foreach(@uc_list){
      my $mstr = "$uc_head"."_([0-9]+)\$";
      if( $_ =~ m/$mstr/ ){ if( $1 > $max ){ $max = $1; } }	# 一番大きい数字を調べる
    }

    my $num = sprintf("%03d",($max+1));		# 一番大きい数字＋１を付ける
    $name = $head."_$num";
  }
  return $name;
}

###################################################################################################
1;
