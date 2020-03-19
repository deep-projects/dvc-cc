


# TEST DT-CLUSTER


python simple_tensorflow_test.py --gitprojectname TESTI --gitpath https://dagshub.com --num_of_repeats_of_each_run 1 mastaer annusch
python simple_tensorflow_test.py --gitprojectname TESTI  --num_of_repeats_of_each_run 1 annusch annusch

python papermill_without_output.py --gitprojectname TESTI --num_of_repeats_of_each_run 1 annusch annusch
python papermill_with_output.py --gitprojectname TESTI  --num_of_repeats_of_each_run 1 annusch annusch


python sshfs_test.py --gitprojectname TESTI  --num_of_repeats_of_each_run 1 annusch annusch dt1.f4.htw-berlin.de:/mnt
dt1.f4.htw-berlin.de:/mnt dt1.f4.htw-berlin.de:/mnt/md0/annusch






python student_credentials.py --gitprojectname TESTI --num_of_repeats_of_each_run 1 annusch s0000000

python student_credentials.py --gitprojectname TESTI --num_of_repeats_of_each_run 1 annusch s0000001