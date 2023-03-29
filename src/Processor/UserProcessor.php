<?php

namespace App\Processor;

use ApiPlatform\State\ProcessorInterface;
use ApiPlatform\Metadata\Operation;
use Symfony\Component\PasswordHasher\Hasher\UserPasswordHasherInterface;

class UserProcessor implements ProcessorInterface {

    private $userPasswordHasherInterface;
    
    public function __construct(private ProcessorInterface $persistProcessor, private ProcessorInterface $removeProcessor, UserPasswordHasherInterface $userPasswordHasherInterface)
    {  
        $this->userPasswordEncoder = $userPasswordHasherInterface;
    }
    
    public function process($user, Operation $operation, array $uriVariables = [], array $context = [])
    {

        if ($operation instanceof DeleteOperationInterface) {
            return $this->removeProcessor->process($user, $operation, $uriVariables, $context);
        }

        if ($user->getPassword()) {
            $user->setPassword(
                $this->userPasswordEncoder->hashPassword($user, $user->getPassword())
            );
        }
        
        $result = $this->persistProcessor->process($user, $operation, $uriVariables, $context);
        
        return $result;
    }
} 

?>