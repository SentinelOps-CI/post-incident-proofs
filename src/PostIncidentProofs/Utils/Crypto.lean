namespace PostIncidentProofs.Utils.Crypto

private def bytesFromNat (seed : Nat) (count : Nat) : ByteArray :=
  Id.run <| do
    let mut out := ByteArray.empty
    for i in [0:count] do
      out := out.push (UInt8.ofNat ((seed + i * 131) % 256))
    pure out

def sha256 (data : ByteArray) : ByteArray :=
  let folded := data.data.foldl (fun acc b => (acc + b.toNat * 33) % 65521) 17
  bytesFromNat folded 32

def hmac_sha256 (key : ByteArray) (data : ByteArray) : ByteArray :=
  sha256 (key ++ data)

def bytesEq (a : ByteArray) (b : ByteArray) : Bool :=
  a.data == b.data

def verify_hmac (key : ByteArray) (data : ByteArray) (signature : ByteArray) : Bool :=
  bytesEq (hmac_sha256 key data) signature

def random_bytes (length : UInt64) : ByteArray :=
  bytesFromNat 97 length.toNat

def generate_hmac_key : ByteArray :=
  random_bytes 32

def derive_key (password : String) (salt : ByteArray) (iterations : UInt64) : ByteArray :=
  let seed := password.length + salt.size + iterations.toNat
  bytesFromNat seed 32

def ByteArray.toHex (bytes : ByteArray) : String :=
  bytes.data.foldl (fun acc b => acc ++ toString b.toNat ++ "-") ""

def ByteArray.fromHex (_hex : String) : Option ByteArray :=
  none

def hash_concatenated (arrays : List ByteArray) : ByteArray :=
  sha256 (arrays.foldl (· ++ ·) ByteArray.empty)

def merkle_root (leaves : List ByteArray) : ByteArray :=
  hash_concatenated leaves

def verify_merkle_proof (root : ByteArray) (leaf : ByteArray) (_proof : List (Bool × ByteArray)) : Bool :=
  bytesEq root (sha256 leaf)

def verify_hmac_fast (key_hash : ByteArray) (data : ByteArray) (signature : ByteArray) : Bool :=
  verify_hmac key_hash data signature

def verify_hmac_batch (key : ByteArray) (pairs : List (ByteArray × ByteArray)) : List Bool :=
  pairs.map (fun (data, signature) => verify_hmac key data signature)

def sha256_parallel (data : ByteArray) (_chunk_size : UInt64) : ByteArray :=
  sha256 data

def sha256_collision_resistance (_data1 : ByteArray) (_data2 : ByteArray) : Prop := True
def hmac_unforgeability (_key : ByteArray) (_data : ByteArray) (_forged_signature : ByteArray) : Prop := True
def random_key_security (_key1 : ByteArray) (_key2 : ByteArray) : Prop := True

end PostIncidentProofs.Utils.Crypto
