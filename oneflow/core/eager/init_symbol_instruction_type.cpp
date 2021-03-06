/*
Copyright 2020 The OneFlow Authors. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/
#include "oneflow/core/common/util.h"
#include "oneflow/core/vm/init_symbol_instruction_type.h"
#include "oneflow/core/job/job_desc.h"
#include "oneflow/core/job/scope.h"
#include "oneflow/core/operator/op_conf.pb.h"
#include "oneflow/core/operator/op_attribute.pb.h"

namespace oneflow {
namespace eager {

COMMAND(Global<vm::SymbolStorage<Scope>>::SetAllocated(new vm::SymbolStorage<Scope>()));
using ScopeInstr = vm::InitSymbolInstructionType<Scope>;
COMMAND(vm::RegisterInstructionType<ScopeInstr>("InitScopeSymbol"));

COMMAND(Global<vm::SymbolStorage<JobDesc>>::SetAllocated(new vm::SymbolStorage<JobDesc>()));
using JobDescInstr = vm::InitSymbolInstructionType<JobDesc>;
COMMAND(vm::RegisterInstructionType<JobDescInstr>("InitJobDescSymbol"));

COMMAND(
    Global<vm::SymbolStorage<OperatorConf>>::SetAllocated(new vm::SymbolStorage<OperatorConf>()));
using OperatorConfInstr = vm::InitSymbolInstructionType<OperatorConf>;
COMMAND(vm::RegisterInstructionType<OperatorConfInstr>("InitOperatorConfSymbol"));

COMMAND(Global<vm::SymbolStorage<OpNodeSignatureDesc>>::SetAllocated(
    new vm::SymbolStorage<OpNodeSignatureDesc>()));
using OpNodeSignatureInstr = vm::InitSymbolInstructionType<OpNodeSignatureDesc>;
COMMAND(vm::RegisterInstructionType<OpNodeSignatureInstr>("InitOpNodeSignatureDescSymbol"));

}  // namespace eager
}  // namespace oneflow
